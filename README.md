# MailTrack

Minimal email open-tracker. Sends disclosed, tracked emails via Gmail and logs opens through an invisible pixel.

## Setup

```
pip install -r requirements.txt
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export TRACKER_BASE_URL="https://your-public-url"
```

Gmail app password: Google Account -> Security -> 2-Step Verification -> App passwords.

## Run the tracker server

```
python app.py
```

Dashboard at `http://localhost:5000`. Expose it publicly (ngrok, cloud host, etc.) and set `TRACKER_BASE_URL` to that public URL before sending.

## Send a tracked email

```
echo "<p>Hello, this is a test.</p>" > body.html
python send.py --to someone@example.com --subject "Test" --body body.html
```

## How it works

- Every sent email gets a unique tracking ID.
- A 1x1 invisible GIF pixel pointing at `/pixel/<id>.gif` is embedded in the HTML body.
- Every email also includes a visible disclosure line stating it is tracked.
- When the recipient's mail client loads images, the pixel request is logged (time, IP, user-agent) in `tracking.db`.
- View results on the dashboard.

## Note

Image-blocking clients (and plaintext mode) will not trigger the pixel, so opens are a lower bound, not a guarantee.
