import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "contacts.db")


# ============================================================
# SIMPLE .ENV LOADER
# ============================================================

def load_dotenv():
    env_path = os.path.join(BASE_DIR, ".env")

    if not os.path.isfile(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if (
                not line
                or line.startswith("#")
                or "=" not in line
            ):
                continue

            key, value = line.split("=", 1)

            os.environ[key.strip()] = (
                value.strip()
                .strip("'")
                .strip('"')
            )


load_dotenv()


# ============================================================
# EMAIL CONFIGURATION - RESEND
# ============================================================

def get_email_config():
    load_dotenv()

    api_key = os.getenv("RESEND_API_KEY", "").strip()

    notify_email = os.getenv(
        "NOTIFY_EMAIL",
        ""
    ).strip()

    from_email = os.getenv(
        "RESEND_FROM_EMAIL",
        "onboarding@resend.dev"
    ).strip()

    return api_key, notify_email, from_email


# ============================================================
# RATE LIMITING
# ============================================================

RATE_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_IP = 5

RATE_LIMIT = {}


# ============================================================
# DATABASE
# ============================================================

def init_db():
    os.makedirs(
        os.path.dirname(DB_PATH),
        exist_ok=True
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                subject TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()


# ============================================================
# VALIDATION
# ============================================================

def valid_email(value):
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            value or ""
        )
    )


# ============================================================
# SEND EMAIL USING RESEND API
# ============================================================

def send_notification(data):

    api_key, notify_email, from_email = get_email_config()

    # Check configuration
    if not api_key:
        return False, "RESEND_API_KEY is not configured"

    if not notify_email:
        return False, "NOTIFY_EMAIL is not configured"

    # Email content
    subject = (
        data.get("subject")
        or "Contact request"
    )

    email_text = (
        "New enquiry received from "
        "A N Constructions website.\n\n"

        f"Name: {data['name']}\n"
        f"Email: {data['email']}\n"
        f"Phone: {data.get('phone', '')}\n"
        f"Subject: {data.get('subject', '')}\n\n"

        "Message:\n"
        f"{data['message']}\n"
    )

    # Resend API payload
    payload = {
        "from": from_email,
        "to": [notify_email],
        "subject": f"New website enquiry: {subject}",
        "text": email_text
    }

    # Create HTTPS request
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            response_body = response.read().decode(
                "utf-8"
            )

            result = json.loads(
                response_body
            )

            email_id = result.get(
                "id",
                ""
            )

            return (
                True,
                f"Email sent successfully. ID: {email_id}"
            )

    except urllib.error.HTTPError as exc:

        error_body = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        return (
            False,
            f"Resend API error {exc.code}: {error_body}"
        )

    except urllib.error.URLError as exc:

        return (
            False,
            f"Network error: {exc.reason}"
        )

    except Exception as exc:

        return (
            False,
            str(exc)
        )


# ============================================================
# HTTP API HANDLER
# ============================================================

class APIHandler(SimpleHTTPRequestHandler):

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            directory=BASE_DIR,
            **kwargs
        )

    # --------------------------------------------------------
    # RESPONSE HEADERS
    # --------------------------------------------------------

    def end_headers(self):

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        super().end_headers()

    # --------------------------------------------------------
    # JSON RESPONSE
    # --------------------------------------------------------

    def _json(
        self,
        status,
        payload
    ):

        body = json.dumps(
            payload
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(body)

    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        path = urlparse(
            self.path
        ).path

        # Health check
        if path == "/api/health":

            return self._json(
                200,
                {
                    "status": "ok",
                    "database": os.path.exists(
                        DB_PATH
                    )
                }
            )

        # Get saved contacts
        if path == "/api/contacts":

            with sqlite3.connect(
                DB_PATH
            ) as conn:

                conn.row_factory = sqlite3.Row

                rows = [
                    dict(row)
                    for row in conn.execute(
                        """
                        SELECT *
                        FROM contacts
                        ORDER BY id DESC
                        """
                    ).fetchall()
                ]

            return self._json(
                200,
                {
                    "contacts": rows
                }
            )

        # Normal website files
        return super().do_GET()

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def do_POST(self):

        path = urlparse(
            self.path
        ).path

        # Only contact API
        if path != "/api/contact":

            return self._json(
                404,
                {
                    "success": False,
                    "message": "Endpoint not found"
                }
            )

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        client_ip = self.client_address[0]

        now = time.time()

        recent = [
            timestamp
            for timestamp in RATE_LIMIT.get(
                client_ip,
                []
            )
            if now - timestamp
            < RATE_WINDOW_SECONDS
        ]

        if len(recent) >= MAX_REQUESTS_PER_IP:

            return self._json(
                429,
                {
                    "success": False,
                    "message":
                        "Too many requests. "
                        "Please try again later."
                }
            )

        recent.append(now)

        RATE_LIMIT[client_ip] = recent

        # ----------------------------------------------------
        # READ JSON REQUEST
        # ----------------------------------------------------

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            if length > 10000:

                return self._json(
                    413,
                    {
                        "success": False,
                        "message":
                            "Request is too large."
                    }
                )

            raw = self.rfile.read(
                length
            )

            data = json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            return self._json(
                400,
                {
                    "success": False,
                    "message":
                        "Invalid JSON request."
                }
            )

        # ----------------------------------------------------
        # GET FORM DATA
        # ----------------------------------------------------

        name = str(
            data.get("name", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip()

        phone = str(
            data.get("phone", "")
        ).strip()

        subject = str(
            data.get("subject", "")
        ).strip()

        message = str(
            data.get("message", "")
        ).strip()

        # ----------------------------------------------------
        # VALIDATE FORM
        # ----------------------------------------------------

        if not name or len(name) > 100:

            return self._json(
                400,
                {
                    "success": False,
                    "message":
                        "Please enter a valid name."
                }
            )

        if not valid_email(email):

            return self._json(
                400,
                {
                    "success": False,
                    "message":
                        "Please enter a valid email."
                }
            )

        if (
            len(phone) > 30
            or len(subject) > 200
            or not message
            or len(message) > 5000
        ):

            return self._json(
                400,
                {
                    "success": False,
                    "message":
                        "Please check the submitted fields."
                }
            )

        # ----------------------------------------------------
        # SAVE TO SQLITE
        # ----------------------------------------------------

        try:

            with sqlite3.connect(
                DB_PATH
            ) as conn:

                cursor = conn.execute(
                    """
                    INSERT INTO contacts
                    (
                        name,
                        email,
                        phone,
                        subject,
                        message
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        phone,
                        subject,
                        message
                    )
                )

                contact_id = cursor.lastrowid

                conn.commit()

        except Exception as exc:

            return self._json(
                500,
                {
                    "success": False,
                    "message":
                        "Unable to save your enquiry.",
                    "error": str(exc)
                }
            )

        # ----------------------------------------------------
        # SEND EMAIL
        # ----------------------------------------------------

        email_sent = False
        email_error = None

        try:

            email_sent, email_error = (
                send_notification(
                    {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "subject": subject,
                        "message": message
                    }
                )
            )

        except Exception as exc:

            email_error = str(exc)

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return self._json(
            201,
            {
                "success": True,
                "message":
                    "Thank you. Your enquiry "
                    "has been received.",
                "id": contact_id,
                "email_sent": email_sent,
                "email_status":
                    email_error
                    or "Email sent successfully"
            }
        )


# ============================================================
# SERVER CONFIGURATION
# ============================================================

HOST = os.getenv(
    "HOST",
    "0.0.0.0"
)

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    init_db()

    os.chdir(BASE_DIR)

    print(
        f"A N Constructions server "
        f"running at http://{HOST}:{PORT}"
    )

    print(
        f"Health check: "
        f"http://{HOST}:{PORT}/api/health"
    )

    print(
        f"Contact API: POST "
        f"http://{HOST}:{PORT}/api/contact"
    )

    print(
        f"Saved enquiries DB: "
        f"{DB_PATH}"
    )

    # Email configuration status
    api_key, notify_email, from_email = (
        get_email_config()
    )

    if api_key and notify_email:

        print(
            "Email Notifications: ENABLED "
            f"(sending to {notify_email})"
        )

    else:

        print(
            "Email Notifications: NOT CONFIGURED"
        )

    # Start server
    server = ThreadingHTTPServer(
        (HOST, PORT),
        APIHandler
    )

    print(
        "Server started successfully."
    )

    server.serve_forever()