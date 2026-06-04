"""
管理员后台 API：用户数据统计 + 知识库管理（含 MD5 去重 + 内容查看）
"""
import os
import csv
import hashlib
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.auth import require_admin
from backend.database import get_admin_stats, get_all_users_with_stats, get_user_chat_history
from utils.path_tools import get_abs_path
from utils.config_handler import chroma_config
from utils.logger_handler import logger

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== 统计与用户数据 ====================

@router.get("/stats")
def admin_stats(user: dict = Depends(require_admin)):
    return get_admin_stats()


@router.get("/users")
def admin_users(user: dict = Depends(require_admin)):
    """获取所有用户列表（含会话统计 + CSV 使用数据）"""
    users = get_all_users_with_stats()

    csv_path = get_abs_path("data/external/records.csv")
    csv_data = {}
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row.get("用户ID", "").strip('"').strip()
                if uid not in csv_data:
                    csv_data[uid] = []
                csv_data[uid].append({
                    "特征": row.get("特征", "").strip('"').strip(),
                    "清洁效率": row.get("清洁效率", "").strip('"').strip(),
                    "耗材": row.get("耗材", "").strip('"').strip(),
                    "对比": row.get("对比", "").strip('"').strip(),
                    "时间": row.get("时间", "").strip('"').strip(),
                })

    result = []
    for u in users:
        uid = str(u["id"])
        result.append({
            "id": u["id"],
            "username": u["username"],
            "role": "user",  # users 表全是普通用户，管理员在 admins 表
            "created_at": str(u["created_at"]) if u["created_at"] else None,
            "session_count": u["session_count"],
            "message_count": u["message_count"],
            "csv_records": csv_data.get(uid, []),
        })

    return {"users": result}


@router.get("/users/{user_id}/chats")
def admin_user_chats(user_id: int, user: dict = Depends(require_admin)):
    return {"chats": get_user_chat_history(user_id)}


# ==================== 知识库管理 ====================

def _compute_md5(file_path: str) -> str:
    """计算文件 MD5"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def _get_all_knowledge_files(data_path: str, allowed: list[str]) -> list[dict]:
    """列出知识库文件（含 MD5）"""
    files = []
    if os.path.isdir(data_path):
        for f in sorted(os.listdir(data_path)):
            fpath = os.path.join(data_path, f)
            if os.path.isfile(fpath):
                ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                if ext in allowed:
                    size = os.path.getsize(fpath)
                    md5 = _compute_md5(fpath)
                    files.append({
                        "name": f,
                        "size": size,
                        "size_str": f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB",
                        "md5": md5,
                    })
    return files


@router.get("/knowledge")
def list_knowledge(user: dict = Depends(require_admin)):
    data_path = get_abs_path(chroma_config.get("data_path", "data"))
    allowed = chroma_config.get("allow_knowledge_file_type", ["pdf", "txt"])
    files = _get_all_knowledge_files(data_path, allowed)
    return {"files": files, "data_path": data_path}


@router.get("/knowledge/{filename}/content")
def view_knowledge_content(filename: str, user: dict = Depends(require_admin)):
    """查看知识库文件内容"""
    data_path = get_abs_path(chroma_config.get("data_path", "data"))
    file_path = os.path.join(data_path, filename)

    # 防路径穿越
    real = os.path.realpath(file_path)
    data_real = os.path.realpath(data_path)
    if not real.startswith(data_real):
        raise HTTPException(status_code=403, detail="不允许的操作")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"filename": filename, "type": "text", "content": content}
        elif ext == "pdf":
            # PDF 不直接展示，返回提示
            size = os.path.getsize(file_path)
            return {"filename": filename, "type": "pdf",
                    "content": f"[PDF 文件，大小: {size / 1024:.1f} KB]",
                    "hint": "PDF 内容暂不支持在线预览，请下载后查看"}
        else:
            return {"filename": filename, "type": "unknown", "content": "不支持预览此文件类型"}
    except Exception as e:
        return {"filename": filename, "type": "error", "content": f"读取失败: {str(e)}"}


@router.post("/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), user: dict = Depends(require_admin)):
    """上传文档到知识库（含 MD5 去重检查）"""
    data_path = get_abs_path(chroma_config.get("data_path", "data"))
    allowed = chroma_config.get("allow_knowledge_file_type", ["pdf", "txt"])

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: .{ext}")

    os.makedirs(data_path, exist_ok=True)

    content = await file.read()
    new_md5 = hashlib.md5(content).hexdigest()

    # MD5 去重：检查是否与已有文件内容一致
    existing_files = _get_all_knowledge_files(data_path, allowed)
    for ef in existing_files:
        if ef["md5"] == new_md5:
            return {
                "ok": False,
                "duplicate": True,
                "existing_file": ef["name"],
                "message": f"该文档内容已加入知识库，无需重复添加，见文档「{ef['name']}」",
            }

    # 不重复：保存文件
    save_path = os.path.join(data_path, file.filename)
    base, fext = os.path.splitext(file.filename)
    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(data_path, f"{base}_{counter}{fext}")
        counter += 1

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "ok": True,
        "duplicate": False,
        "filename": os.path.basename(save_path),
        "size": len(content),
        "message": f"文档「{os.path.basename(save_path)}」上传成功",
    }


@router.delete("/knowledge/{filename}")
def delete_knowledge(filename: str, user: dict = Depends(require_admin)):
    data_path = get_abs_path(chroma_config.get("data_path", "data"))
    file_path = os.path.join(data_path, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    real = os.path.realpath(file_path)
    data_real = os.path.realpath(data_path)
    if not real.startswith(data_real):
        raise HTTPException(status_code=403, detail="不允许的操作")

    os.remove(file_path)
    return {"ok": True, "filename": filename}


@router.post("/knowledge/reload")
def reload_knowledge(user: dict = Depends(require_admin)):
    md5_path = get_abs_path(chroma_config.get("md5_hex_store", "md5.text"))
    try:
        if os.path.exists(md5_path):
            os.remove(md5_path)
        return {"ok": True, "message": "MD5 记录已清除，下次加载知识库时将重新索引所有文档"}
    except Exception as e:
        return {"ok": False, "message": str(e)}
