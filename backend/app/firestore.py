import os
from uuid import uuid4
from .utils import utc_now

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    firebase_admin = None

class MemoryStore:
    def __init__(self):
        self.data = {"users": {}, "establishments": {}, "services": {}, "queueEntries": {}, "queueCounters": {}, "staffAssignments": {}}
        from .seed import seed
        seed(self)
    def get(self, collection, id): return self.data[collection].get(id)
    def create(self, collection, doc):
        id = doc.get("id", uuid4().hex); item = {"id": id, **doc}; self.data[collection][id] = item; return item
    def update(self, collection, id, updates):
        if id not in self.data[collection]: raise LookupError(id)
        self.data[collection][id].update(updates); return self.data[collection][id]
    def list(self, collection): return list(self.data[collection].values())
    def next_sequence(self, service_id):
        counter = self.data["queueCounters"].get(service_id, {"id": service_id, "lastSequence": 0}); counter["lastSequence"] += 1; counter["updatedAt"] = utc_now(); self.data["queueCounters"][service_id] = counter; return counter["lastSequence"]
    def find_active_for_user(self, service_id, user_id):
        return next((q for q in self.data["queueEntries"].values() if q["serviceId"] == service_id and q["userId"] == user_id and q["status"] in {"WAITING", "CALLED", "SERVING"}), None)
    def count_active(self, service_id): return sum(q["serviceId"] == service_id and q["status"] in {"WAITING", "CALLED", "SERVING"} for q in self.data["queueEntries"].values())
    def count_ahead(self, service_id, sequence): return sum(q["serviceId"] == service_id and q["status"] in {"WAITING", "CALLED"} and q["queueSequence"] < sequence for q in self.data["queueEntries"].values())
    def history(self, user_id): return sorted([q for q in self.data["queueEntries"].values() if q["userId"] == user_id], key=lambda x: x["createdAt"], reverse=True)

def create_store():
    project = os.getenv("FIREBASE_PROJECT_ID") or os.getenv("GCLOUD_PROJECT")
    if not project or not firebase_admin:
        return MemoryStore()
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()
    return FirestoreStore(db)

class FirestoreStore(MemoryStore):
    def __init__(self, db): self.db = db
    def get(self, collection, id):
        snap = self.db.collection(collection).document(id).get(); return snap.to_dict() | {"id": snap.id} if snap.exists else None
    def create(self, collection, doc):
        id = doc.get("id") or str(uuid4()); item={"id": id, **{k:v for k,v in doc.items() if k != "id"}}; self.db.collection(collection).document(id).set(item); return item
    def update(self, collection, id, updates):
        ref=self.db.collection(collection).document(id); ref.update(updates); return self.get(collection,id)
    def list(self, collection): return [{"id": s.id, **s.to_dict()} for s in self.db.collection(collection).stream()]
    def next_sequence(self, service_id):
        ref=self.db.collection("queueCounters").document(service_id)
        @firestore.transactional
        def txn(transaction):
            snap=ref.get(transaction=transaction); value=snap.to_dict()["lastSequence"]+1 if snap.exists else 1; transaction.set(ref,{"lastSequence":value,"updatedAt":utc_now()}); return value
        return txn(self.db.transaction())
    def find_active_for_user(self, service_id, user_id):
        for q in self.db.collection("queueEntries").where("serviceId","==",service_id).where("userId","==",user_id).stream():
            item={"id":q.id,**q.to_dict()};
            if item["status"] in {"WAITING","CALLED","SERVING"}: return item
    def count_active(self, service_id): return sum(1 for _ in self.db.collection("queueEntries").where("serviceId","==",service_id).where("status","in",["WAITING","CALLED","SERVING"]).stream())
    def count_ahead(self,service_id,sequence): return sum(1 for q in self.db.collection("queueEntries").where("serviceId","==",service_id).stream() if q.to_dict()["status"] in {"WAITING","CALLED"} and q.to_dict()["queueSequence"]<sequence)
    def history(self,user_id): return [{"id":q.id,**q.to_dict()} for q in self.db.collection("queueEntries").where("userId","==",user_id).order_by("createdAt",direction=firestore.Query.DESCENDING).stream()]
