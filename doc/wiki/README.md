# Digital Cafe Wiki

## Current State

The repository contains the initial Django scaffold for the Digital Cafe application. The Django project is named `digitalcafe`, and the initial application boundary is the `core` app.

The requested e-commerce features are not implemented yet. The current application remains Django's generated welcome page.

The scaffold is merged into `main`. Django's system check passes, and the default welcome page returns HTTP 200 from the local development server.

## Local Setup

The project uses the repository-local Python virtual environment at `env/`, which is intentionally ignored by git. Activate it before running Django commands:

```bash
source env/bin/activate
```

The local database is SQLite and `db.sqlite3` is ignored. The development server can be started with:

```bash
python manage.py runserver
```

## Workflow

Feature work follows the process documented in `AGENTS.md`: study, plan, execute the plan on a branch, rendezvous by merging and pushing `main`, and sync the wiki documentation.
