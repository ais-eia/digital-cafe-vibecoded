# Auth Navigation Plan

## Branch and Scope

- [x] Confirm the working tree and preserve unrelated user changes before implementation.
- [x] Create a focused auth-navigation branch from current `main`.
- [x] Keep this feature limited to shared authenticated navigation and logout.
- [x] Do not change credentials, registration, password reset, admin navigation, authorization rules, or existing business behavior.

## Shared Navigation Template

- [x] Add `core/templates/core/base.html` with a shared navigation marker and page-content block.
- [x] Add named links for home/catalog, cart, checkout, and transaction history.
- [x] Display the current authenticated username.
- [x] Add a POST logout form with `{% csrf_token %}` and `{% url 'logout' %}` action.
- [x] Keep the login template standalone so it does not inherit the authenticated navigation.
- [ ] Convert every authenticated application template to extend the base:
  - [x] Home
  - [x] Product detail
  - [x] Cart
  - [x] Checkout
  - [x] Checkout confirmation
  - [x] Transaction history
- [x] Preserve each page's existing content and empty/error states.

## Logout Route and Redirect

- [x] Add a named `/logout/` URL using Django's built-in `LogoutView`.
- [x] Configure logout to redirect to the unprefixed `/login/` target so Coderange prefixes the response once.
- [x] Keep the logout action POST-only through the navigation form.
- [x] Do not add custom session-clearing logic.
- [x] Ensure admin navigation remains controlled by Django admin templates and is not replaced by the public base template.

## Tests

- [x] Assert the navigation appears on authenticated home, product detail, cart, checkout, checkout confirmation, and transaction history pages.
- [x] Assert the navigation includes home, cart, checkout, and transaction-history links.
- [x] Assert the navigation displays the authenticated username.
- [x] Assert the logout control is a POST form with a CSRF token and named logout action.
- [x] Assert the login page returns HTTP 200 but contains no navigation marker, username navigation, or logout control.
- [x] POST logout as an authenticated user and assert it redirects to the login URL.
- [x] Assert logout invalidates the session and protected pages redirect to login afterward.
- [x] Assert GET `/logout/` does not perform logout or create an authenticated-navigation regression.
- [x] Test prefix-aware generated navigation and logout action URLs with `/proxy/8000` configured.
- [x] Preserve all existing authentication, catalog, cart, checkout, history, admin, and redirect-prefix tests.

## Verification and Documentation

- [x] Run `python manage.py check` with the prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [ ] Manually verify authenticated navigation and logout through the Coderange UI. Automated navigation/logout coverage passes; interactive verification remains.
- [x] Verify the login page has no authenticated navigation.
- [x] Verify post-logout access to protected pages requires login.
- [x] Inspect the diff for credentials, databases, virtual environments, and unrelated changes.
- [x] Commit implementation with a Conventional Commit message such as `feat: add auth navigation`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the navigation branch, tests, and commit history.
- [ ] Merge the auth-navigation branch into `main` without overwriting unrelated changes.
- [ ] Re-run checks, the full test suite, and Coderange navigation/logout smoke verification on merged `main`.
- [ ] Confirm the merged application starts and logout invalidates authenticated sessions.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with shared navigation links, POST logout behavior, login-page exclusion, and verification commands.
