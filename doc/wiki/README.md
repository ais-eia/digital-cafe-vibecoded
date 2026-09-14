# Digital Cafe Wiki

## Current State

The repository contains the Django application for Digital Cafe. The Django project is named `digitalcafe`, and the application boundary is the `core` app.

User authentication is implemented with Django's built-in `User` model and native username/password authentication. The application root is protected and currently displays a greeting for the logged-in user. Product catalog, cart, checkout, transaction history, and product administration features are not implemented yet.

The authentication feature is merged into `main`. Django's system check and five authentication tests pass. The login page returns HTTP 200, and anonymous requests to the protected root redirect to `/login/?next=/`.

## Authentication

- `/login/` displays the native username/password login form.
- Invalid credentials are shown as a visible form error.
- Successful login redirects to `/`.
- `/` requires authentication and greets the user by username.
- The coderange forwarding origin is trusted for Django CSRF protection during development.

The login flow uses Django's session middleware and built-in authentication middleware. Create users through Django's standard admin or management commands; user registration is not part of the current feature.

## Local Setup

The project uses the repository-local Python virtual environment at `env/`, which is intentionally ignored by git. Activate it before running Django commands:

```bash
source env/bin/activate
```

The local database is SQLite and `db.sqlite3` is ignored. The development server can be started with:

```bash
python manage.py runserver
```

Run the authentication checks with:

```bash
python manage.py check
python manage.py test core
```

## Workflow

Feature work follows the process documented in `AGENTS.md`: study, plan, execute the plan on a branch, rendezvous by merging and pushing `main`, and sync the wiki documentation.
