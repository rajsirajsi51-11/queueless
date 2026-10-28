# Security

The frontend sends Firebase ID tokens to Flask. Flask verifies tokens, reads the trusted role from the user document, and checks ownership and staff assignment. The request role cannot grant privileges.

Customers cannot write queue documents directly; browser writes are denied by `firebase/firestore.rules`. Admin SDK credentials stay on the backend and are never included in frontend environment variables.

Development mode exposes demo accounts through `X-Dev-Uid` and is intended only on a local machine. Disable it in production with `DEV_AUTH_ENABLED=false`.

Additional deployment hardening should include secret rotation, provider rate limits, Firebase App Check, audit logging, and HTTPS-only origins.
