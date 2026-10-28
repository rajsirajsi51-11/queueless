from datetime import datetime, timezone
from .utils import utc_now

ACTIVE_STATUSES = {"WAITING", "CALLED", "SERVING"}

class QueueService:
    def __init__(self, store):
        self.store = store

    def join(self, user_id, service_id, request_id=None):
        service = self.store.get("services", service_id)
        if not service or service["status"] != "ACTIVE":
            raise ValueError("Service is unavailable")
        existing = self.store.find_active_for_user(service_id, user_id)
        if existing:
            return existing, False
        waiting = self.store.count_active(service_id)
        if waiting >= service["maxQueueSize"]:
            raise ValueError("This queue is full")
        sequence = self.store.next_sequence(service_id)
        ticket = {
            "userId": user_id, "serviceId": service_id,
            "ticketNumber": f"{service.get('code', 'T')}-{sequence}",
            "queueSequence": sequence, "status": "WAITING",
            "createdAt": utc_now(), "version": 1,
            "requestId": request_id
        }
        ticket = self.store.create("queueEntries", ticket)
        return ticket, True

    def position(self, ticket):
        if ticket["status"] not in ACTIVE_STATUSES:
            return 0
        ahead = self.store.count_ahead(ticket["serviceId"], ticket["queueSequence"])
        service = self.store.get("services", ticket["serviceId"])
        minutes = ahead * service["estimatedServiceMinutes"]
        return {"position": ahead + 1, "peopleAhead": ahead, "estimatedWaitMinutes": minutes}

    def transition(self, ticket_id, from_status, to_status, allowed_roles=("STAFF", "ADMIN")):
        ticket = self.store.get("queueEntries", ticket_id)
        if not ticket:
            raise LookupError("Ticket not found")
        if ticket["status"] != from_status:
            raise ValueError("Ticket status changed; refresh and try again")
        now = utc_now()
        updates = {"status": to_status, "version": ticket["version"] + 1}
        field = {"CALLED": "calledAt", "SERVING": "serviceStartedAt",
                 "COMPLETED": "completedAt", "CANCELLED": "cancelledAt",
                 "NO_SHOW": "cancelledAt"}.get(to_status)
        if field:
            updates[field] = now
        return self.store.update("queueEntries", ticket_id, updates)
