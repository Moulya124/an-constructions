# A N Constructions — Backend Connected

The website now includes a working contact form connected to:

**Contact Form → Python API → SQLite Database → Email Notification**

## Requirements

- Python 3.9+
- No external Python packages are required.

## 1. Configure email

Copy `.env.example` to `.env` and fill in your SMTP settings.

For Gmail, use:
- SMTP_HOST=smtp.gmail.com
- SMTP_PORT=587
- SMTP_USER=your Gmail address
- SMTP_PASSWORD=your Gmail App Password
- NOTIFY_EMAIL=the inbox that should receive enquiries

Do not use your normal Gmail password. Create a Google App Password after enabling 2-Step Verification.

## 2. Run

Windows PowerShell:

```powershell
python backend.py
```

Then open:

http://127.0.0.1:3000/

Contact page:

http://127.0.0.1:3000/pages/contact.html

## 3. Test the API

Open:

http://127.0.0.1:3000/api/health

You should see JSON similar to:

```json
{"status":"ok","database":true}
```

## 4. Database

The first run automatically creates:

`data/contacts.db`

Submitted enquiries are stored in the `contacts` table.

For local/admin testing, saved enquiries can be viewed at:

http://127.0.0.1:3000/api/contacts

Important: `/api/contacts` is intentionally unauthenticated for local development. Add authentication before deploying this endpoint publicly.

## Email behavior

The enquiry is inserted into SQLite first. Then the server attempts to send the notification email.

Therefore, if SMTP is temporarily unavailable, the enquiry is still saved in the database.

## Production note

Before deploying publicly:
- Add authentication to `/api/contacts`.
- Use HTTPS.
- Put the backend behind a production web server/reverse proxy.
- Move secrets to secure environment variables.
- Add stronger rate limiting and CSRF/origin controls as appropriate.
