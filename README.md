# Ridevo

**Know before you buy.**

Ridevo is a project focused on helping people make more informed decisions when buying used cars. The goal is to analyse vehicle listings, identify potential risks, and provide useful insights before a purchase.

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Testing:** Pytest

## Current Features

- FastAPI application setup
- Health check endpoint
- Database readiness check
- PostgreSQL connection

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ertugakmann/ridevo.git
cd ridevo
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure your database connection:

```env
APP_NAME=Ridevo API
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/ridevo
```

Replace `YOUR_PASSWORD` with your local PostgreSQL password.

### 5. Run the API

```bash
python -m uvicorn app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks whether the API is running |
| GET | `/ready` | Checks database connectivity |
| GET | `/docs` | Interactive API documentation |

## Running Tests

```bash
python -m pytest
```

## Roadmap

- [ ] Vehicle report data model
- [ ] Database migrations
- [ ] Vehicle report creation and retrieval endpoints
- [ ] Used car listing analysis
- [ ] Vehicle risk scoring
- [ ] AI-powered report generation

## Status

Ridevo is currently under active development. Features and architecture may change as the project evolves.