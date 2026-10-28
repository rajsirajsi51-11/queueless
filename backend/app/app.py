import os
from flask import Flask, request, g
from flask_cors import CORS
from .config import Config
from .firestore import create_store
from .queue_service import QueueService
from .auth import require_auth, require_role
from .utils import ok, fail

def create_app(config=None):
    app=Flask(__name__)
    app.config.from_object(Config)
    if config: app.config.update(config)
    CORS(app, origins=app.config["CORS_ORIGINS"])
    store=create_store(); service=QueueService(store)
    auth=require_auth(store, app.config["DEV_AUTH_ENABLED"])

    @app.get("/api/v1/health")
    def health(): return ok({"status":"healthy"})
    @app.get("/api/v1/ready")
    def ready(): return ok({"status":"ready","database":"configured" if os.getenv("FIREBASE_PROJECT_ID") else "in-memory development mode"})
    @app.get("/api/v1/me")
    @auth
    def me(): return ok(g.user)
    @app.get("/api/v1/establishments")
    def establishments(): return ok(store.list("establishments"))
    @app.get("/api/v1/establishments/<id>")
    def establishment(id): return ok(store.get("establishments",id)) if store.get("establishments",id) else fail("Establishment not found",404,"NOT_FOUND")
    @app.get("/api/v1/services")
    def services(): return ok(store.list("services"))
    @app.get("/api/v1/services/<id>")
    def one_service(id): return ok(store.get("services",id)) if store.get("services",id) else fail("Service not found",404,"NOT_FOUND")

    @app.post("/api/v1/queue")
    @auth
    def join():
        if g.user["role"] != "CUSTOMER": return fail("Customers only",403,"FORBIDDEN")
        payload=request.get_json(silent=True) or {}; service_id=payload.get("serviceId")
        if not isinstance(service_id,str) or not service_id.strip(): return fail("serviceId is required")
        try:
            ticket, created=service.join(g.uid,service_id.strip(),request.headers.get("Idempotency-Key"))
            return ok({"ticket":ticket,"created":created},201 if created else 200)
        except ValueError as e: return fail(str(e),409 if "already" in str(e).lower() else 400)

    def owned(ticket): return ticket and (ticket["userId"] == g.uid or g.user["role"] in {"STAFF","ADMIN"})
    @app.get("/api/v1/queue/<ticket_id>")
    @auth
    def ticket(ticket_id):
        item=store.get("queueEntries",ticket_id)
        return ok(item) if owned(item) else fail("Ticket not found",404,"NOT_FOUND")
    @app.get("/api/v1/queue/<ticket_id>/position")
    @auth
    def position(ticket_id):
        item=store.get("queueEntries",ticket_id)
        if not owned(item): return fail("Ticket not found",404,"NOT_FOUND")
        return ok(service.position(item))
    @app.post("/api/v1/queue/<ticket_id>/cancel")
    @auth
    def cancel(ticket_id):
        item=store.get("queueEntries",ticket_id)
        if not item or item["userId"] != g.uid: return fail("Ticket not found",404,"NOT_FOUND")
        if item["status"] not in {"WAITING","CALLED"}: return fail("This ticket can no longer be cancelled",409,"INVALID_TRANSITION")
        try: return ok(service.transition(ticket_id,item["status"],"CANCELLED"))
        except ValueError as e: return fail(str(e),409,"STALE_STATUS")
    @app.get("/api/v1/me/queue-history")
    @auth
    def history(): return ok(store.history(g.uid))

    def assigned(ticket):
        if g.user["role"]=="ADMIN": return True
        assignment_id=f"{g.uid}-{ticket['serviceId']}"
        return bool(store.get("staffAssignments",assignment_id))
    @app.get("/api/v1/staff/queue")
    @auth
    @require_role("STAFF","ADMIN")
    def staff_queue():
        service_id=request.args.get("serviceId")
        items=[q for q in store.list("queueEntries") if (not service_id or q["serviceId"]==service_id) and (g.user["role"]=="ADMIN" or q["serviceId"] in [a["serviceId"] for a in store.list("staffAssignments") if a["staffUserId"]==g.uid])]
        return ok(items)
    def staff_action(ticket_id,target):
        ticket=store.get("queueEntries",ticket_id)
        if not ticket: return fail("Ticket not found",404,"NOT_FOUND")
        if not assigned(ticket): return fail("You are not assigned to this service",403,"FORBIDDEN")
        expected={"CALL":"WAITING","START":"CALLED","COMPLETE":"SERVING","NO_SHOW":"CALLED"}[target]
        status={"CALL":"CALLED","START":"SERVING","COMPLETE":"COMPLETED","NO_SHOW":"NO_SHOW"}[target]
        try: return ok(service.transition(ticket_id,expected,status))
        except ValueError as e: return fail(str(e),409,"INVALID_TRANSITION")
    @app.post("/api/v1/staff/queue/<ticket_id>/call")
    @auth
    @require_role("STAFF","ADMIN")
    def call(ticket_id): return staff_action(ticket_id,"CALL")
    @app.post("/api/v1/staff/queue/<ticket_id>/start")
    @auth
    @require_role("STAFF","ADMIN")
    def start(ticket_id): return staff_action(ticket_id,"START")
    @app.post("/api/v1/staff/queue/<ticket_id>/complete")
    @auth
    @require_role("STAFF","ADMIN")
    def complete(ticket_id): return staff_action(ticket_id,"COMPLETE")
    @app.post("/api/v1/staff/queue/<ticket_id>/no-show")
    @auth
    @require_role("STAFF","ADMIN")
    def no_show(ticket_id): return staff_action(ticket_id,"NO_SHOW")
    @app.patch("/api/v1/staff/services/<service_id>/status")
    @auth
    @require_role("STAFF","ADMIN")
    def service_status(service_id):
        item=store.get("services",service_id)
        if not item or not assigned({"serviceId":service_id}): return fail("Service not found or not assigned",404,"NOT_FOUND")
        status=(request.get_json(silent=True) or {}).get("status")
        if status not in {"ACTIVE","PAUSED"}: return fail("Status must be ACTIVE or PAUSED")
        return ok(store.update("services",service_id,{"status":status}))

    @app.errorhandler(413)
    def too_large(_): return fail("Request body is too large",413,"REQUEST_TOO_LARGE")
    app.config["MAX_CONTENT_LENGTH"] = 64*1024
    app.extensions["store"] = store
    return app
