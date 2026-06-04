"""
FastAPI 后端 —— 用户认证 + 会话管理 + SSE 流式聊天（带记忆）
"""
import json
import sys
import asyncio
import threading
from pathlib import Path

# 确保项目根在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent.react_agent import ReactAgent
from backend.auth import router as auth_router, get_current_user
from backend.admin import router as admin_router
from backend.database import (
    create_session,
    get_user_sessions,
    get_session,
    delete_session,
    get_session_messages,
    save_message,
    update_session_title,
)

app = FastAPI(title="智扫通机器人智能客服 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载认证路由和管理员路由
app.include_router(auth_router)
app.include_router(admin_router)


# ==================== 会话管理 ====================

@app.get("/api/sessions")
def list_sessions(user: dict = Depends(get_current_user)):
    """获取当前用户的所有会话"""
    sessions = get_user_sessions(user["id"])
    return {"sessions": sessions}


@app.post("/api/sessions")
def new_session(user: dict = Depends(get_current_user)):
    """创建新会话"""
    sid = create_session(user["id"])
    return {"id": sid, "title": "新对话"}


@app.delete("/api/sessions/{session_id}")
def remove_session(session_id: int, user: dict = Depends(get_current_user)):
    """删除会话"""
    sess = get_session(session_id)
    if not sess or sess["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="会话不存在")
    delete_session(session_id)
    return {"ok": True}


@app.get("/api/sessions/{session_id}/messages")
def load_messages(session_id: int, user: dict = Depends(get_current_user)):
    """加载会话历史消息"""
    sess = get_session(session_id)
    if not sess or sess["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="会话不存在")
    msgs = get_session_messages(session_id)
    return {"messages": msgs}


# ==================== 聊天（带记忆） ====================

@app.post("/api/chat")
async def chat(request: Request, user: dict = Depends(get_current_user)):
    """
    SSE 流式聊天
    请求体: {"message": "...", "session_id": N}
    响应:  SSE 流，data 行带 type: thinking/answer
    """
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id")

    if not message.strip():
        return StreamingResponse(
            _empty_stream("请输入消息内容"),
            media_type="text/event-stream",
        )

    # 如果没有 session_id，自动创建
    if not session_id:
        session_id = create_session(user["id"])
    else:
        sess = get_session(session_id)
        if not sess or sess["user_id"] != user["id"]:
            raise HTTPException(status_code=404, detail="会话不存在")

    # 加载历史消息作为 Agent 的记忆上下文
    history = get_session_messages(session_id, limit=20)

    # 存储当前用户消息
    save_message(session_id, "user", message)

    # 自动更新会话标题（取用户第一条消息的前 20 字）
    current_sess = get_session(session_id)
    if current_sess and current_sess["title"] == "新对话":
        title = message[:20] + ("..." if len(message) > 20 else "")
        update_session_title(session_id, title)

    async def event_stream():
        agent = ReactAgent()
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        # 收集助手最终回答内容
        answer_chunks = []

        def run_sync():
            try:
                for event in agent.execute_stream_typed(message, history, user_id=str(user["id"])):
                    asyncio.run_coroutine_threadsafe(
                        queue.put(("chunk", event)), loop
                    )
                asyncio.run_coroutine_threadsafe(queue.put(("done", None)), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put(("error", str(e))), loop
                )

        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()

        try:
            while True:
                op, value = await queue.get()
                if op == "done":
                    break
                if op == "error":
                    payload = json.dumps(
                        {"type": "error", "content": f"系统错误：{value}"},
                        ensure_ascii=False,
                    )
                    yield f"data: {payload}\n\n"
                    break
                if op == "chunk":
                    if value.get("type") == "answer":
                        answer_chunks.append(value["content"])
                    payload = json.dumps(value, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
        finally:
            thread.join(timeout=5)

        # 流结束后，将助手回答存入 MySQL
        full_answer = "".join(answer_chunks).strip()
        if full_answer:
            save_message(session_id, "assistant", full_answer)

        # 发送 session_id（前端可能需要）
        meta = json.dumps({"type": "meta", "session_id": session_id}, ensure_ascii=False)
        yield f"data: {meta}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _empty_stream(msg: str):
    payload = json.dumps({"content": msg}, ensure_ascii=False)
    yield f"data: {payload}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
