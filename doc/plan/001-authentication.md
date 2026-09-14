# User Authentication Plan

## Branch and Scope

- [x] Confirm the working tree and preserve the existing unrelated `digitalcafe/settings.py` change.
- [x] Create a focused feature branch from the current `main` branch before implementation.
- [x] Keep this feature limited to native username/password login, authenticated home access, and related tests; do not implement products, carts, checkout, transactions, registration, password reset, or admin customization.

## Application Views and URLs

- [x] Add a `core` home view protected by Django's `login_required` decorator.
- [x] Render the authenticated user's username in the home page greeting.
- [x] Add the root URL `/` for the protected home view.
- [x] Add `/login/` using Django's built-in `LoginView` and `AuthenticationForm`.
- [x] Set the login success destination to `/` and the unauthenticated redirect target to `/login/` without replacing Django's safe `next` handling.

## Templates

- [x] Create a minimal project-owned login template under the `core` app template directory.
- [x] Render username and password inputs using the bound Django authentication form.
- [x] Render field-level errors and `form.non_field_errors` so invalid credentials produce a visible error message.
- [x] Create a minimal home template that displays the logged-in user's username.
- [x] Keep templates dependency-free and avoid introducing frontend frameworks or unrelated styling.

## Tests

- [x] Add tests using Django's test client and built-in `User` model.
- [x] Verify an anonymous request to `/` redirects to `/login/?next=/`.
- [x] Verify `/login/` returns HTTP 200 and includes username and password fields.
- [x] Verify invalid credentials return the login page with a visible authentication error.
- [x] Verify valid credentials authenticate the session, redirect to `/`, and display the username greeting.
- [x] Verify an authenticated user can access `/`.
- [x] Ensure tests use isolated test data and do not require a committed local database.

## Verification and Documentation

- [x] Run the required migrations against the ignored local SQLite database if authentication tables are not present.
- [x] Run `python manage.py check`.
- [x] Run the relevant Django test suite and confirm all authentication tests pass.
- [x] Start the development server and manually verify the login page, failed-login message, and authenticated greeting.
- [x] Inspect the diff to confirm no virtual environment, SQLite database, credentials, or unrelated settings changes are staged.
- [x] Commit implementation changes with a Conventional Commit message such as `feat: add user authentication`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the feature branch and commit history before rendezvous.
- [ ] Merge the feature branch into `main` without overwriting unrelated user changes.
- [ ] Re-run Django checks and authentication tests on merged `main`.
- [ ] Confirm the merged application starts and serves the authentication flow.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the authentication URLs, behavior, local verification commands, and current feature state.
