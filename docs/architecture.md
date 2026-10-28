# Architecture

```mermaid
flowchart LR
  Browser --> React
  React -->|REST + ID token| Flask
  Flask --> Firestore
  React -->|authorized listeners| Firestore
  Browser --> FirebaseAuth[Firebase Authentication]
  Flask --> AdminSDK[Firebase Admin SDK]
  GitHub --> Actions[GitHub Actions]
  Actions --> FrontendHost[Frontend hosting]
  Actions --> BackendHost[Backend hosting]
```

React handles presentation. Flask is the authoritative queue API. Firebase Authentication verifies identity. Firestore stores tickets and allows authorized real-time reads. Firebase Security Rules add direct-browser protection. The Admin SDK is only used server-side.

## Joining flow

```mermaid
sequenceDiagram
  Customer->>React: Choose service
  React->>Flask: POST /api/v1/queue
  Flask->>FirebaseAuth: Verify ID token
  Flask->>Firestore: Transactionally allocate sequence and ticket
  Firestore-->>React: Listener receives ticket update
```
