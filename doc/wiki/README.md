# Digital Cafe Wiki

## Current State

The repository contains the Django application for Digital Cafe. The Django project is named `digitalcafe`, and the application boundary is the `core` app.

User authentication is implemented with Django's built-in `User` model and native username/password authentication. The application root is protected and displays a greeting plus the product catalog for the logged-in user. Product cart, checkout, transaction history, and product administration features are not implemented yet.

The authentication and product browsing features are merged into `main`. Django's system check passes and 17 tests pass in both direct-root and Coderange-prefix configurations. With the default Coderange configuration, anonymous requests redirect to `/proxy/8000/login/?next=/proxy/8000/` and generated application links remain under `/proxy/8000/`.

## Authentication

- `/login/` displays the native username/password login form.
- Invalid credentials are shown as a visible form error.
- Successful login redirects to `/`.
- `/` requires authentication and greets the user by username.
- The coderange forwarding origin is trusted for Django CSRF protection during development.

## Product Browsing

- `/` displays the authenticated user's greeting and a table of products.
- `/products/<id>/` displays a product's name, price, and a link back to the catalog.
- Unknown product IDs return HTTP 404.
- Anonymous users are redirected to the prefixed login URL.
- Optional sample products are available through `core/fixtures/products.json` and can be loaded with `python manage.py loaddata products`.

## Coderange Proxy Prefix

Coderange exposes the app at `/proxy/8000/` and, based on the available direct request diagnostics plus the working UI verification, is expected to strip that prefix before forwarding requests to Django. Django is configured with an environment-backed script name:

```bash
DJANGO_SCRIPT_NAME=/proxy/8000
```

The default is `/proxy/8000`. For direct local development without the sandbox prefix, use an empty value:

```bash
DJANGO_SCRIPT_NAME='' python manage.py runserver
```

Do not include `/proxy/8000` in URLconf patterns or templates. Use Django URL reversing so generated paths include the configured script prefix exactly once.

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

For the Coderange deployment, the default command generates prefixed URLs. For direct local access, use the `DJANGO_SCRIPT_NAME=''` command above.

Run the authentication checks with:

```bash
python manage.py check
python manage.py test core
```

## Workflow

Feature work follows the process documented in `AGENTS.md`: study, plan, execute the plan on a branch, rendezvous by merging and pushing `main`, and sync the wiki documentation.
