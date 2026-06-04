from langchain.agents import create_agent
from agent.tools.agent_tools import *
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from langchain_core.messages import AIMessage, ToolMessage

class ReactAgent():
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            tools = [get_weather, get_user_location, rag_summarize, fetch_external_data,get_current_month,get_user_id],
            system_prompt = load_system_prompt(),
            middleware = [monitor_tool, log_before_model, report_prompt_switch]
        )

    def execute_stream(self, query: str):
        """原始流式输出（兼容旧代码，保留给 Streamlit 使用）"""
        input_dict = {"messages": [
            {"role": "user", "content": query}
        ]}

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"

    def execute_stream_typed(self, query: str, history: list[dict] | None = None, user_id: str | None = None):
        """
        带类型的流式输出，区分「思考过程」和「最终回答」
        history: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        user_id: 当前登录用户的 ID，注入到 Agent 上下文
        yield: {"type": "thinking", "content": "..."} | {"type": "answer", "content": "..."}
        """
        from agent.tools.agent_tools import set_current_user_id, clear_current_user_id

        try:
            # 先清除上一轮可能残留的 user_id（防止线程复用污染）
            clear_current_user_id()
            if user_id:
                set_current_user_id(user_id)

            # 构建消息列表：用户上下文 + 历史消息 + 当前问题
            messages = []
            if user_id:
                messages.append({
                    "role": "system",
                    "content": f"当前登录用户ID为: {user_id}。当用户要求生成报告、查询自己的数据、或需要用户信息时，直接使用此ID，不得询问用户。"
                })
            if history:
                for msg in history:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": query})

            input_dict = {"messages": messages}

            for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
                latest_message = chunk["messages"][-1]

                # 跳过无内容的消息
                if not latest_message.content:
                    continue

                content = latest_message.content.strip()

                # ToolMessage → 工具返回结果，属于思考过程
                if isinstance(latest_message, ToolMessage):
                    yield {"type": "thinking", "content": content}
                    continue

                # AIMessage 有 tool_calls → Agent 正在决策调用工具，属于思考过程
                if isinstance(latest_message, AIMessage) and getattr(latest_message, "tool_calls", None):
                    yield {"type": "thinking", "content": content}
                    continue

                # AIMessage 无 tool_calls → 最终回答
                if isinstance(latest_message, AIMessage):
                    yield {"type": "answer", "content": content}
                    continue

                # 兜底：其他消息类型按普通内容处理
                yield {"type": "answer", "content": content}
        finally:
            # 流结束后清理线程局部变量，防止下个请求污染
            clear_current_user_id()


if __name__ == "__main__":
    react_agent = ReactAgent()
    query = "给我生成我的使用报告，我的ID为1001"
    for chunk in react_agent.execute_stream_typed(query):
        label = "🧠 思考" if chunk["type"] == "thinking" else "✅ 回答"
        print(f"[{label}] {chunk['content']}", end="", flush=True)
            