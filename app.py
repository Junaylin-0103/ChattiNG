import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads") if app.static_folder else "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

socketio = SocketIO(app, cors_allowed_origins="*")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DB_PATH = "database.db"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Junaylin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change_this_password")

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/webm"}


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            banned INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

    ensure_admin_account()


def ensure_admin_account():
    conn = get_db()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
    if user is None:
        conn.execute(
            "INSERT INTO users (username, password_hash, banned) VALUES (?, ?, 0)",
            (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD)),
        )
        conn.commit()
    conn.close()


def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def verify_csrf():
    token = request.form.get("csrf_token")
    return bool(token) and token == session.get("csrf_token")


def is_banned(username):
    conn = get_db()
    row = conn.execute("SELECT banned FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row is not None and row["banned"] == 1


def require_login(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if is_banned(session["user"]):
            session.clear()
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


@app.before_request
def before_request():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not verify_csrf():
            return "CSRF token invalid", 400

        action = request.form.get("action", "login")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "用户名和密码不能为空", 400

        conn = get_db()

        if action == "register":
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                conn.close()
                return "用户名已存在", 400

            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            conn.commit()
            conn.close()

            session["user"] = username
            return redirect(url_for("chat"))

        if action == "login":
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()

            if not user:
                return "用户不存在", 404

            if user["banned"] == 1:
                return "你已被禁止使用该聊天室", 403

            if not check_password_hash(user["password_hash"], password):
                return "密码错误", 401

            session["user"] = username
            return redirect(url_for("chat"))

        return "无效操作", 400

    return render_template("index.html")


@app.route("/chat")
@require_login
def chat():
    return render_template("index.html")


@app.route("/logout", methods=["POST"])
def logout():
    if not verify_csrf():
        return "CSRF token invalid", 400
    session.clear()
    return redirect(url_for("login"))


@app.route("/ban", methods=["POST"])
def ban_user():
    if not verify_csrf():
        return "CSRF token invalid", 400

    if session.get("user") != ADMIN_USERNAME:
        return "无权限", 403

    target_username = request.form.get("username", "").strip()
    if not target_username:
        return "请输入要封禁的用户名", 400

    conn = get_db()
    conn.execute("UPDATE users SET banned = 1 WHERE username = ?", (target_username,))
    conn.commit()
    conn.close()
    return f"{target_username} 已被封禁。"


@socketio.on("load_history")
def load_history():
    user = session.get("user")
    if not user:
        emit("error", {"message": "未登录"})
        return

    conn = get_db()
    rows = conn.execute(
        "SELECT user, type, content, created_at FROM messages ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "user": row["user"],
            "type": row["type"],
            "content": row["content"],
            "created_at": row["created_at"],
        })

    emit("history", {"messages": list(reversed(history))})


@socketio.on("message")
def handle_message(data):
    user = session.get("user")
    if not user:
        emit("error", {"message": "未登录"})
        return

    if is_banned(user):
        emit("error", {"message": "你已被禁止使用该聊天室"})
        return

    if not isinstance(data, dict):
        emit("error", {"message": "无效消息"})
        return

    msg_type = data.get("type")
    content = data.get("content", "")

    if msg_type not in {"text", "image", "voice"}:
        emit("error", {"message": "不支持的消息类型"})
        return

    if not isinstance(content, str):
        emit("error", {"message": "消息内容必须为字符串"})
        return

    if msg_type == "text":
        if len(content) > 2000:
            emit("error", {"message": "文本消息过长"})
            return
    else:
        if len(content) > 5 * 1024 * 1024:
            emit("error", {"message": "文件过大"})
            return
        if not content.startswith("data:"):
            emit("error", {"message": "无效文件内容"})
            return

    payload = {"user": user, "type": msg_type, "content": content}

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (user, type, content) VALUES (?, ?, ?)",
        (user, msg_type, content),
    )
    conn.commit()
    conn.close()

    emit("message", payload, broadcast=True)


if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)


























































































































"""
Project: ChattiNG
Summary: Real-time chat app with Flask + SocketIO + SQLite
"""











































































































































































































































































































