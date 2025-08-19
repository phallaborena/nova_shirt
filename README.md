# Nova Shirt

A minimal Flask shop for a course project.

## Pages
- **Home** (`/`) – shows all products.
- **Products** (`/products`) – grouped into 3 sections: Shirts, Pants, Shoes.
- **About** (`/about`) – intro and 4 team profiles.
- **Cart** (`/cart`) – view/update/remove items.
- **Payment** (`/checkout`) – enter details and submit payment; sends Telegram notification with order summary.

## Quick Start (local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# set env vars (PowerShell example)
$env:TELEGRAM_BOT_TOKEN="your-bot-token"
$env:TELEGRAM_CHAT_ID="your-chat-id"
python app.py
```

Open http://127.0.0.1:5000

## Render.com Deploy
1. Create a new **Web Service** from this repo/folder.
2. Runtime: Python; Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Add environment variables from `.env.example` (at least the Telegram ones).

## Logo
Replace `static/logo-placeholder.png` with your own logo image (keep the file name or update the `<img>` path in `templates/base.html`).

## Edit team names
Open `templates/about.html` and change the four names/roles/bios.
