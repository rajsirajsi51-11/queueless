# QueueLess

A full-stack real-time queue management portfolio project.

## Local setup

```powershell
python -m pip install -r backend/requirements.txt
cd backend
python main.py
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The demo runs without Firebase credentials using clearly marked development accounts. Use the demo login page to switch between customer, staff, and admin roles.

## Documentation

- [Architecture](docs/architecture.md)
- [Database design](docs/database-design.md)
- [Queue algorithms](docs/queue-algorithms.md)
- [Security](docs/security.md)
- [Deployment](docs/deployment.md)
- [Viva guide](docs/viva-guide.md)

Production Firebase configuration variables are listed in `.env.example`. Never commit credentials.
