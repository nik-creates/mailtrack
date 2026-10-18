"""
Flask server: serves the tracking pixel + a dashboard to view opens.
"""
from flask import Flask, Response, request, render_template
import db

app = Flask(__name__)

# 1x1 transparent GIF
PIXEL = bytes.fromhex(
    "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
)


@app.before_request
def _init():
    db.init_db()


@app.route("/pixel/<tracking_id>.gif")
def pixel(tracking_id):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    db.log_open(tracking_id, ip, ua)
    resp = Response(PIXEL, mimetype="image/gif")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/")
def dashboard():
    emails = db.get_all_emails()
    return render_template("dashboard.html", emails=emails)


@app.route("/email/<tracking_id>")
def email_detail(tracking_id):
    opens = db.get_opens_for_email(tracking_id)
    return render_template("detail.html", tracking_id=tracking_id, opens=opens)


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
