from functools import wraps
from flask import request, g
from .utils import fail

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
except ImportError:
    firebase_admin = None

def require_auth(store, dev_enabled=True):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            token = header[7:] if header.startswith("Bearer ") else None
            uid = None
            if dev_enabled:
                uid = request.headers.get("X-Dev-Uid")
            if not uid and token:
                try:
                    decoded = firebase_auth.verify_id_token(token)
                    uid = decoded["uid"]
                except Exception:
                    return fail("Invalid or expired authentication token", 401, "UNAUTHENTICATED")
            if not uid:
                return fail("Authentication required", 401, "UNAUTHENTICATED")
            user = store.get("users", uid)
            if not user:
                return fail("User profile not found", 403, "FORBIDDEN")
            g.uid, g.user = uid, user
            return fn(*args, **kwargs)
        return wrapped
    return decorator

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if getattr(g, "user", {}).get("role") not in roles:
                return fail("You do not have permission for this action", 403, "FORBIDDEN")
            return fn(*args, **kwargs)
        return wrapped
    return decorator
