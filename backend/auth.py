"""
认证相关路由：注册 / 登录 / 获取当前用户
支持分离的 users 表和 admins 表
"""
import hashlib
import secrets
from fastapi import APIRouter, HTTPException, Header, Depends
from backend.database import (
    get_user_by_username,
    get_admin_by_username,
    get_user_by_token,
    create_user,
    create_token_with_role,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """pbkdf2_hmac 加盐哈希"""
    salt = b"agent_rag_salt_2024"
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return dk.hex()


def generate_token() -> str:
    return secrets.token_hex(32)


def get_current_user(authorization: str = Header(None)) -> dict:
    """FastAPI 依赖：从 Authorization header 解析用户（user 或 admin）"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization[7:]
    result = get_user_by_token(token)
    if not result:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return {
        "id": result["id"],
        "username": result["username"],
        "role": result["role"],
        "token": token,
    }


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """FastAPI 依赖：要求管理员权限"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@router.post("/register")
def register(body: dict):
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4位")

    existing = get_user_by_username(username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user_id = create_user(username, hash_password(password))
    token = generate_token()
    create_token_with_role(user_id, token, "user")

    return {"user_id": user_id, "username": username, "token": token, "role": "user"}


@router.post("/login")
def login(body: dict):
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()
    role = (body.get("role") or "user").strip()  # 前端传入的角色选择

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    if role == "admin":
        # 管理员登录：查 admins 表
        admin = get_admin_by_username(username)
        if not admin or admin["password_hash"] != hash_password(password):
            raise HTTPException(status_code=401, detail="管理员用户名或密码错误")
        token = generate_token()
        create_token_with_role(admin["id"], token, "admin")
        return {"user_id": admin["id"], "username": admin["username"], "token": token, "role": "admin"}
    else:
        # 普通用户登录：查 users 表
        user = get_user_by_username(username)
        if not user or user["password_hash"] != hash_password(password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        token = generate_token()
        create_token_with_role(user["id"], token, "user")
        return {"user_id": user["id"], "username": user["username"], "token": token, "role": "user"}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"user_id": user["id"], "username": user["username"], "role": user["role"]}
