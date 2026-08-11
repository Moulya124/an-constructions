import json
import os
import re
import sqlite3
import smtplib
import time
from email.message import EmailMessage
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "contacts.db")

def load_dotenv():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")

load_dotenv()


def get_smtp_config():
    load_dotenv()
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    notify = os.getenv("NOTIFY_EMAIL", user)
    return host, port, user, password, notify

RATE_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_IP = 5
RATE_LIMIT = {}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                subject TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value or ""))

def send_notification(data):
    smtp_host, smtp_port, smtp_user, smtp_password, notify_email = get_smtp_config()
    if not all([smtp_host, smtp_user, smtp_password, notify_email]):
        return False, "SMTP is not configured"

    msg = EmailMessage()
    msg["Subject"] = f"New website enquiry: {data.get('subject') or 'Contact request'}"
    msg["From"] = smtp_user
    msg["To"] = notify_email
    msg.set_content(
        "New enquiry received from A N Constructions website.\n\n"
        f"Name: {data['name']}\n"
        f"Email: {data['email']}\n"
        f"Phone: {data.get('phone', '')}\n"
        f"Subject: {data.get('subject', '')}\n"
        f"Message:\n{data['message']}\n"
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
    return True, "Email sent"


class APIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(200, {"status": "ok", "database": os.path.exists(DB_PATH)})
        if path == "/api/contacts":
            # Local/admin convenience endpoint. Do not expose publicly without authentication.
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = [dict(r) for r in conn.execute(
                    "SELECT * FROM contacts ORDER BY id DESC"
                ).fetchall()]
            return self._json(200, {"contacts": rows})
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/contact":
            return self._json(404, {"success": False, "message": "Endpoint not found"})

        client_ip = self.client_address[0]
        now = time.time()
        recent = [t for t in RATE_LIMIT.get(client_ip, []) if now - t < RATE_WINDOW_SECONDS]
        if len(recent) >= MAX_REQUESTS_PER_IP:
            return self._json(429, {"success": False, "message": "Too many requests. Please try again later."})
        recent.append(now)
        RATE_LIMIT[client_ip] = recent

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 10000:
                return self._json(413, {"success": False, "message": "Request is too large."})
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._json(400, {"success": False, "message": "Invalid JSON request."})

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        phone = str(data.get("phone", "")).strip()
        subject = str(data.get("subject", "")).strip()
        message = str(data.get("message", "")).strip()

        if not name or len(name) > 100:
            return self._json(400, {"success": False, "message": "Please enter a valid name."})
        if not valid_email(email):
            return self._json(400, {"success": False, "message": "Please enter a valid email."})
        if len(phone) > 30 or len(subject) > 200 or not message or len(message) > 5000:
            return self._json(400, {"success": False, "message": "Please check the submitted fields."})

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """INSERT INTO contacts (name, email, phone, subject, message)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, email, phone, subject, message)
            )
            contact_id = cursor.lastrowid
            conn.commit()

        email_sent = False
        email_error = None
        try:
            email_sent, email_error = send_notification({
                "name": name, "email": email, "phone": phone,
                "subject": subject, "message": message
            })
        except Exception as exc:
            email_error = str(exc)

        return self._json(201, {
            "success": True,
            "message": "Thank you. Your enquiry has been received.",
            "id": contact_id,
            "email_sent": email_sent,
            "email_status": email_error or "Email sent"
        })

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))

if __name__ == "__main__":
    init_db()
    os.chdir(BASE_DIR)
    print(f"A N Constructions server running at http://{HOST}:{PORT}")
    print(f"Health check: http://{HOST}:{PORT}/api/health")
    print(f"Contact API: POST http://{HOST}:{PORT}/api/contact")
    print(f"Saved enquiries DB: {DB_PATH}")
    smtp_host, smtp_port, smtp_user, smtp_password, notify_email = get_smtp_config()
    if all([smtp_host, smtp_user, smtp_password, notify_email]):
        print(f"SMTP Notifications: ENABLED (sending to {notify_email})")
    else:
        print("SMTP Notifications: NOT CONFIGURED (Create .env file with SMTP_USER and SMTP_PASSWORD)")
    ThreadingHTTPServer((HOST, PORT), APIHandler).serve_forever()


