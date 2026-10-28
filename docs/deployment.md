# Deployment

## Firebase

1. Create a Firebase project and enable Authentication and Firestore.
2. Add web app configuration to frontend environment variables.
3. Create a backend service account secret or configure hosting workload identity.
4. Deploy rules and indexes with `firebase deploy --only firestore`.
5. Seed roles and data using a controlled backend script; never expose admin credentials.

## Render-style backend

Set the variables from `.env.example`, deploy `backend/Dockerfile`, start Gunicorn, set `DEV_AUTH_ENABLED=false`, and configure exact CORS origins.

## Vercel-style frontend

Set the `VITE_*` variables, deploy the `frontend` directory, and set `VITE_API_BASE_URL` to the verified public HTTPS API URL.

No public URL can be stated until credentials and hosting accounts are available. Deployment is therefore BLOCKED outside this workspace.
