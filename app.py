from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from urllib.parse import quote

app = Flask(__name__)

API_BASE = os.environ.get("API_BASE", "https://robingquestbio.vercel.app")
API_UID  = os.environ.get("API_UID", "4429701975")
API_PASS = os.environ.get("API_PASS", "ARAFAT-CODEX-SAMIDUF5RPHH7")

TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", "35"))


def success_from_api(payload: dict) -> bool:
    # Your API uses: "✅ Success"
    status_val = str(payload.get("status", "")).strip().lower()
    return "success" in status_val


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.get("/style.css")
def css():
    return send_from_directory(".", "style.css")


@app.get("/ping")
def ping():
    return jsonify({"ok": True, "pong": True})


@app.get("/test-api")
def test_api():
    # Quick server-side test: confirms Vercel can reach API
    test_bio = request.args.get("bio", "TEST_OK")
    url = f"{API_BASE.rstrip('/')}/bio_upload?bio={quote(test_bio)}&uid={quote(API_UID)}&pass={quote(API_PASS)}"
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,*/*"})
        try:
            payload = r.json()
        except Exception:
            return jsonify({
                "ok": False,
                "reason": "API did not return JSON",
                "http_status": r.status_code,
                "preview": (r.text or "")[:400],
                "url_used": url
            }), 200

        return jsonify({
            "ok": True,
            "http_status": r.status_code,
            "api_status": payload.get("status"),
            "api_code": payload.get("code"),
            "raw": payload,
            "url_used": url
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "reason": str(e), "url_used": url}), 200


@app.post("/update")
def update():
    data = request.get_json(silent=True) or {}
    bio = (data.get("bio") or "").strip()
    if not bio:
        return jsonify({"ok": False, "message": "Bio cannot be empty."}), 200

    url = f"{API_BASE.rstrip('/')}/bio_upload?bio={quote(bio)}&uid={quote(API_UID)}&pass={quote(API_PASS)}"

    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,*/*"})
        try:
            payload = r.json()
        except Exception:
            return jsonify({
                "ok": False,
                "message": "Update unsuccessful!",
                "reason": "API did not return JSON to Vercel",
                "http_status": r.status_code,
                "preview": (r.text or "")[:400],
                "url_used": url
            }), 200

        ok = success_from_api(payload)
        return jsonify({
            "ok": ok,
            "message": "Update successful!" if ok else "Update unsuccessful!",
            "api_status": payload.get("status"),
            "api_code": payload.get("code"),
            "raw": payload,
            "url_used": url
        }), 200

    except Exception as e:
        return jsonify({"ok": False, "message": "Update unsuccessful!", "reason": str(e), "url_used": url}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
