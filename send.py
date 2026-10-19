"""
Send a tracked email via Gmail SMTP.

Usage:
    python send.py --to someone@example.com --subject "Hi" --body body.html
    python send.py --to someone@example.com --subject "Hi" --text "Email text message"

Required env vars:
    GMAIL_ADDRESS      your gmail address
    GMAIL_APP_PASSWORD gmail app password (not your normal password)
    TRACKER_BASE_URL   public URL of the running Flask app, e.g. https://your-domain.com

Every email includes an invisible 1x1 pixel that logs opens against a unique ID.
"""
import argparse
import os
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import db


def send_tracked_email(to_addr: str, subject: str, html_body: str):
    gmail_addr = os.environ["GMAIL_ADDRESS"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    base_url = os.environ["TRACKER_BASE_URL"].rstrip("/")

    tracking_id = uuid.uuid4().hex
    pixel_tag = f"<img src='{base_url}/pixel/{tracking_id}.gif' width='1' height='1' style='display:none;' alt=''>"

    full_html = f"{html_body}\n{pixel_tag}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(full_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_addr, gmail_pass)
        server.sendmail(gmail_addr, to_addr, msg.as_string())

    db.init_db()
    db.register_email(tracking_id, to_addr, subject)
    print(f"Sent. tracking_id={tracking_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True, help="recipient email address")
    parser.add_argument("--subject", required=True, help="email subject line")
    parser.add_argument("--body", required=False, help="path to an HTML body file")
    parser.add_argument("--text", required=False, help="direct inline text/HTML body string")
    args = parser.parse_args()

    if args.body:
        with open(args.body) as f:
            html_body = f.read()
    elif args.text:
        html_body = f"<p>{args.text}</p>" if not args.text.strip().startswith("<") else args.text
    else:
        raise ValueError("Either --body or --text must be provided")

    send_tracked_email(args.to, args.subject, html_body)
