# Digital Cafe Wiki

## Current State

The repository contains the Django application for Digital Cafe. The Django project is named `digitalcafe`, and the application boundary is the `core` app.

User authentication is implemented with Django's built-in `User` model and native username/password authentication. The application root is protected and displays a greeting plus the product catalog for the logged-in user. Product cart, checkout, transaction history, and product administration features are not implemented yet.

Authentication, product browsing, shopping cart, and redirect-prefix handling are merged into `main`. Django's system check passes and 32 tests pass in both direct-root and Coderange-prefix configurations. With the default Coderange configuration, generated HTML links remain under `/proxy/8000/`, while redirect responses use unprefixed Django paths for Coderange to prefix exactly once.

## Authentication

- `/login/` displays the native username/password login form.
- Invalid credentials are shown as a visible form error.
- Successful login redirects to `/`.
- `/` requires authentication and greets the user by username.
- The coderange forwarding origin is trusted for Django CSRF protection during development.
- Application redirects use unprefixed paths because Coderange automatically prefixes redirect `Location` headers.

## Shopping Cart

- Authenticated users can add a product from `/products/<id>/` with a quantity from 1 through 99.
- Repeated additions increment the existing user/product cart row.
- `/cart/` displays the current user's products, unit prices, quantities, and line totals.
- Cart rows are persisted in SQLite through the `CartItem` model and isolated by authenticated user.
- Product deletion is protected while a cart row references the product.
- Checkout, cart update/remove controls, purchases, and transaction history are not implemented yet.

Application-generated named redirects should use `core.utils.redirect_without_script_prefix()` rather than Django's plain `redirect()` while the Coderange prefix configuration is active. This keeps redirect headers unprefixed for the proxy while preserving `FORCE_SCRIPT_NAME` for normal template URL generation.

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

Load representative products for manual cart verification with:

```bash
python manage.py loaddata products
```

## Workflow

Feature work follows the process documented in `AGENTS.md`: study, plan, execute the plan on a branch, rendezvous by merging and pushing `main`, and sync the wiki documentation.
