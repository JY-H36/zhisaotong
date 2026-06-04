"""
MySQL 连接池 + 增删改查
"""
import pymysql
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "020306",
    "database": "agent_rag",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


@contextmanager
def get_conn():
    """获取数据库连接（上下文管理器，自动提交/关闭）"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== 用户相关 ====================

def get_user_by_token(token: str) -> dict | None:
    """通过 token 获取用户/管理员信息（auth_tokens 含 role 列）"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT t.user_id AS id, t.role FROM auth_tokens t WHERE t.token = %s",
            (token,),
        )
        row = cur.fetchone()
        if not row:
            return None
        # 根据 role 从对应表查用户名
        if row["role"] == "admin":
            cur.execute("SELECT username FROM admins WHERE id = %s", (row["id"],))
            admin = cur.fetchone()
            return {"id": row["id"], "username": admin["username"] if admin else "admin", "role": "admin"}
        else:
            cur.execute("SELECT username FROM users WHERE id = %s", (row["id"],))
            user = cur.fetchone()
            return {"id": row["id"], "username": user["username"] if user else "unknown", "role": "user"}


def get_user_by_username(username: str) -> dict | None:
    """查询 users 表"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        return cur.fetchone()


def get_admin_by_username(username: str) -> dict | None:
    """查询 admins 表"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM admins WHERE username = %s", (username,))
        return cur.fetchone()


def create_user(username: str, password_hash: str) -> int:
    """创建普通用户，返回 user_id"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash),
        )
        return cur.lastrowid


def create_token_with_role(user_id: int, token: str, role: str) -> None:
    """创建 token 并记录角色"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO auth_tokens (user_id, token, role) VALUES (%s, %s, %s)",
            (user_id, token, role),
        )


def delete_token(token: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM auth_tokens WHERE token = %s", (token,))


# ==================== 会话相关 ====================

def create_session(user_id: int, title: str = "新对话") -> int:
    """创建会话，返回 session_id"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessions (user_id, title) VALUES (%s, %s)",
            (user_id, title),
        )
        return cur.lastrowid


def get_user_sessions(user_id: int) -> list[dict]:
    """获取用户的所有会话列表"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, created_at, updated_at FROM sessions "
            "WHERE user_id = %s ORDER BY updated_at DESC",
            (user_id,),
        )
        return cur.fetchall()


def get_session(session_id: int) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
        return cur.fetchone()


def delete_session(session_id: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE id = %s", (session_id,))


def update_session_title(session_id: int, title: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE sessions SET title = %s WHERE id = %s", (title, session_id))


# ==================== 消息相关 ====================

def save_message(session_id: int, role: str, content: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, role, content),
        )


def get_session_messages(session_id: int, limit: int = 20) -> list[dict]:
    """获取会话最近 N 条消息"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (session_id, limit),
        )
        rows = cur.fetchall()
        # 按时间正序返回
        return list(reversed(rows))


def get_last_assistant_message(session_id: int) -> str | None:
    """获取会话最后一条 assistant 消息内容"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT content FROM messages WHERE session_id = %s AND role = 'assistant' "
            "ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        )
        row = cur.fetchone()
        return row["content"] if row else None


# ==================== 管理后台查询 ====================

def get_admin_stats() -> dict:
    """获取管理后台统计数据"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        total_users = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) AS cnt FROM sessions")
        total_sessions = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) AS cnt FROM messages")
        total_messages = cur.fetchone()["cnt"]
        return {
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
        }


def get_all_users_with_stats() -> list[dict]:
    """获取所有普通用户及其会话/消息统计"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT u.id, u.username, u.created_at, "
            "COUNT(DISTINCT s.id) AS session_count, "
            "COUNT(DISTINCT m.id) AS message_count "
            "FROM users u "
            "LEFT JOIN sessions s ON u.id = s.user_id "
            "LEFT JOIN messages m ON s.id = m.session_id "
            "GROUP BY u.id "
            "ORDER BY u.id"
        )
        return cur.fetchall()


def get_user_chat_history(user_id: int, limit: int = 50) -> list[dict]:
    """获取指定用户的聊天记录"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id AS session_id, s.title, m.role, m.content, m.created_at "
            "FROM messages m "
            "JOIN sessions s ON m.session_id = s.id "
            "WHERE s.user_id = %s "
            "ORDER BY m.created_at DESC "
            "LIMIT %s",
            (user_id, limit),
        )
        return cur.fetchall()
