# Viva Guide

## 60-second introduction

QueueLess lets customers join queues without standing in line. React provides the interface, Flask applies trusted queue rules, Firebase Authentication proves identity, Firestore persists tickets, and Firestore listeners update screens in real time. Our complete demo covers joining, staff calling, serving, completion, cancellation, refresh persistence, roles, and live updates.

## Five-minute explanation

The browser calls Flask, which verifies the token and role before changing a ticket. The backend transactionally increments a queue counter and creates an ordered ticket. React reads and listens to Firestore for live state. Security rules enforce direct browser reads and prohibit browser writes; the backend uses Admin SDK credentials, which bypass rules.

## Technology in one line

React builds the interface; Vite runs and builds it; Flask and Gunicorn serve APIs; Firebase Authentication manages users; Firestore stores real-time data; Admin SDK gives trusted backend access; Docker packages services; GitHub Actions tests code.

## Collections and purpose

Users hold profiles and roles; establishments hold locations; services hold queue settings; queue entries hold each ticket; counters hold atomic sequence numbers; assignments connect staff to services.

## Fifteen questions

1. **Why Flask?** Trusted queue rules and authorization need server code.
2. **Authentication or authorization?** Authentication proves who you are; authorization decides what you can do.
3. **How are duplicate tickets prevented?** An active-ticket lookup and request idempotency return one persistent ticket.
4. **How are simultaneous joins safe?** Firestore transactions serialize counter increments.
5. **How are updates real-time?** Browser listeners watch authorized Firestore documents and queries.
6. **Why can JavaScript not grant staff rights?** Roles are stored on the server and protected writes are denied by rules.
7. **What happens after backend restart?** Firestore tickets remain; transient processing restarts and clients reconnect.
8. **What happens offline?** The UI shows errors and the backend cannot process writes.
9. **Is wait time exact?** No; it is a duration estimate based on the average configured service time.
10. **Why are rules needed if Flask checks permissions?** Rules protect direct browser database access.
11. **What is a transaction?** All-or-nothing operations retried safely under concurrency.
12. **What is an API?** A named HTTP endpoint that sends and receives structured JSON.
13. **Why indexes?** They make filtered and ordered queries efficient.
14. **What are the current limitations?** Local demo mode, no payments, no delivery guarantee, and no multi-region deployment.
15. **How would it scale further?** Add cache, queues, observability, and regional infrastructure only if measured demand requires them.

## Demo scenarios

1. Customer joins and refreshes the ticket.
2. Staff calls a ticket and customer sees CALLED.
3. Staff starts and completes service.
4. Customer cancels before service and staff no-shows another ticket.
5. A customer tries a staff endpoint and receives forbidden.

## Important modules

`app.py` defines REST routes; `auth.py` verifies identity and roles; `queue_service.py` owns business rules; `firestore.py` persists and seeds data; React `App.jsx` renders screens and `api.js` calls Flask.
