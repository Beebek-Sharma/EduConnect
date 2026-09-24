# EduConnect

EduConnect is a full-stack educational platform for discovering universities and courses. It combines a Django REST Framework API with a React/Vite frontend and provides separate student and admin workflows.

## Features

- Browse universities and courses
- Search and filter courses
- Compare courses side by side
- Save courses to a personal dashboard
- JWT authentication with access/refresh tokens
- Persistent session and logout handling
- Student and admin roles
- Admin dashboard for universities, courses, and users
- Google OAuth support
- Password reset and email flows
- Interactive Google Maps integration
- Responsive Tailwind CSS interface
- AI chat integration through a configurable API key

## Architecture

```text
EduConnect
├── backend/     Django + Django REST Framework
└── frontend/    React + Vite + Tailwind CSS
```

## Tech stack

### Backend

- Python 3.10+
- Django 5.2
- Django REST Framework
- SimpleJWT
- django-allauth / dj-rest-auth
- SQLite for local development

### Frontend

- React
- Vite
- Tailwind CSS
- Axios
- React Router

## Screenshots

The repository includes application screenshots under `frontend/screenshot/`.

## Local development

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env # macOS/Linux

python manage.py migrate
python manage.py populate_db
python manage.py runserver
```

Backend: `http://127.0.0.1:8000/`

### Frontend

```bash
cd frontend
npm install
copy .env.example .env  # Windows
# cp .env.example .env # macOS/Linux
npm run dev
```

Frontend: `http://localhost:5173/`

## Environment variables

Never commit `.env` files or credentials. The repository contains `.env.example` templates with placeholders for local configuration.

Typical backend variables include:

```env
DJANGO_SECRET_KEY=replace-with-a-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
GROK_API_KEY=your-api-key
```

The frontend uses `VITE_API_URL` to locate the backend API.

## API overview

Authentication includes registration, login, refresh, logout, current-user, and session verification endpoints. Other API areas cover universities, courses, saved courses, users, search, notifications, and the AI chat functionality.

## Production notes

Before deployment, configure production secrets, `DEBUG=False`, allowed hosts, HTTPS, CORS/CSRF origins, secure cookies, a production database, OAuth credentials, and any required third-party API keys.

This repository is a portfolio/development project and should be security-reviewed and configured separately before processing real user data.

## License

MIT
