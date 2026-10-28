import pytest
from app.app import create_app

@pytest.fixture
def client():
    app=create_app({"TESTING":True,"DEV_AUTH_ENABLED":True})
    return app.test_client()

def customer(client): {"X-Dev-Uid":"customer-demo"}
def h(uid): return {"X-Dev-Uid":uid}

def test_health(client):
    assert client.get('/api/v1/health').get_json()['ok'] is True

def test_customer_join_and_position(client):
    r=client.post('/api/v1/queue',json={"serviceId":"general-consultation"},headers=h('customer-demo'))
    assert r.status_code==201
    ticket=r.get_json()['data']['ticket']
    p=client.get(f"/api/v1/queue/{ticket['id']}/position",headers=h('customer-demo'))
    assert p.get_json()['data']['position']==1

def test_duplicate_join(client):
    payload={"serviceId":"document-review"}; headers=h('customer-demo')
    first=client.post('/api/v1/queue',json=payload,headers=headers)
    second=client.post('/api/v1/queue',json=payload,headers=headers)
    assert first.status_code==201 and second.status_code==200
    assert first.get_json()['data']['ticket']['id']==second.get_json()['data']['ticket']['id']

def test_staff_authorization(client):
    join=client.post('/api/v1/queue',json={"serviceId":"general-consultation"},headers=h('customer-demo')).get_json()['data']['ticket']
    denied=client.post(f"/api/v1/staff/queue/{join['id']}/call",headers=h('customer-demo'))
    assert denied.status_code==403
    allowed=client.post(f"/api/v1/staff/queue/{join['id']}/call",headers=h('staff-demo'))
    assert allowed.status_code==200

def test_invalid_status_transition(client):
    join=client.post('/api/v1/queue',json={"serviceId":"document-review"},headers=h('customer-demo')).get_json()['data']['ticket']
    complete=client.post(f"/api/v1/staff/queue/{join['id']}/complete",headers=h('staff-demo'))
    assert complete.status_code==403 # staff is not assigned to document-review

from app.queue_service import QueueService
from app.firestore import MemoryStore

def test_queue_sequence_and_position():
    store=MemoryStore(); queue=QueueService(store)
    first,_=queue.join('customer-demo','general-consultation')
    store.create('users',{'id':'other','role':'CUSTOMER','email':'o@x.com','name':'Other','status':'ACTIVE'})
    second,_=queue.join('other','general-consultation')
    assert second['queueSequence']==first['queueSequence']+1
    assert queue.position(second)['peopleAhead']==1
