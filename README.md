# A N Constructions — Website & Backend

Civil Engineering & Contracting Multi-Page Website + Python API.

## Structure

```
construction/
├── index.html
├── pages/
│   ├── services.html
│   ├── projects.html
│   ├── about.html
│   └── contact.html
├── partials/
│   ├── header.html
│   └── footer.html
├── css/
│   ├── variables.css
│   └── main.css
├── js/
│   ├── include.js
│   ├── main.js
│   └── contact.js
├── data/
│   └── contacts.db       (Auto-created on first run)
├── backend.py
├── .env.example
├── requirements.txt
└── README.md
```

## Running the Project

Start the Python backend server:

```powershell
cd C:\Users\ADMIN\Desktop\Moulya\construction
python backend.py
```

Then visit in your browser:
- Homepage: `http://127.0.0.1:3000/`
- Contact Page: `http://127.0.0.1:3000/pages/contact.html`
- API Health Check: `http://127.0.0.1:3000/api/health`

## Backend Features

- **Framework**: Built using Python 3 standard library (`http.server`). No pip packages required.
- **Single Server Architecture**: Serves frontend static files and API endpoints together on port 3000 to eliminate CORS issues.
- **SQLite Database**: Automatically creates `data/contacts.db` on startup and persists all submitted enquiries to the `contacts` table.
- **Email Notifications**: Automatically sends an SMTP notification email when a new enquiry is submitted. If email configuration is omitted or fails, the enquiry is still securely stored in SQLite.
- **Rate Limiting**: Sliding window rate limiting per IP to prevent spam submissions.

## Environment Configuration

To enable email notifications, copy `.env.example` to `.env` and fill in your SMTP credentials:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFY_EMAIL=your-email@gmail.com
```

## Endpoints

- `GET /api/health` — Checks backend and database status.
- `POST /api/contact` — Submits a contact form enquiry (`name`, `email`, `phone`, `subject`, `message`).
- `GET /api/contacts` — Lists saved enquiries (intended for local administrative reference).

