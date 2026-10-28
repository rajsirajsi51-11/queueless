from datetime import datetime, timezone
from flask import jsonify

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def ok(data=None, status=200):
    return jsonify({"ok": True, "data": data}), status

def fail(message, status=400, code="BAD_REQUEST"):
    return jsonify({"ok": False, "error": {"code": code, "message": message}}), status
