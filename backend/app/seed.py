from .utils import utc_now

def seed(store):
    now=utc_now()
    store.create("users", {"id":"customer-demo","name":"Maya Customer","email":"customer@queueless.local","role":"CUSTOMER","status":"ACTIVE","createdAt":now})
    store.create("users", {"id":"staff-demo","name":"Sam Staff","email":"staff@queueless.local","role":"STAFF","status":"ACTIVE","createdAt":now})
    store.create("users", {"id":"admin-demo","name":"Ari Admin","email":"admin@queueless.local","role":"ADMIN","status":"ACTIVE","createdAt":now})
    store.create("establishments", {"id":"health-center","name":"Campus Health Center","description":"Fast, friendly care on campus","address":"Student Services Building","status":"ACTIVE","createdAt":now})
    store.create("establishments", {"id":"student-office","name":"Student Service Office","description":"Admissions and records assistance","address":"Administration Block","status":"ACTIVE","createdAt":now})
    store.create("services", {"id":"general-consultation","name":"General Consultation","code":"GC","establishmentId":"health-center","status":"ACTIVE","estimatedServiceMinutes":8,"maxQueueSize":30,"createdAt":now})
    store.create("services", {"id":"document-review","name":"Document Review","code":"DR","establishmentId":"student-office","status":"ACTIVE","estimatedServiceMinutes":12,"maxQueueSize":20,"createdAt":now})
    store.create("staffAssignments", {"id":"staff-demo-general-consultation","staffUserId":"staff-demo","serviceId":"general-consultation","establishmentId":"health-center","status":"ACTIVE"})
