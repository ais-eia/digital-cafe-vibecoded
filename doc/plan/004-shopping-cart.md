# Shopping Cart Plan

## Branch and Scope

- [x] Confirm the working tree and preserve any unrelated user changes before implementation.
- [x] Create a focused feature branch from the current `main` branch.
- [x] Keep this feature limited to authenticated cart persistence, add-from-detail behavior, quantity validation, and cart display.
- [x] Do not implement checkout submission, purchases, transaction records, transaction line items, payments, inventory checks, guest carts, product administration, cart update/remove controls, or cart fixtures.

## Cart Model and Migration

- [x] Add a `CartItem` model to `core.models`.
- [x] Reference Django's built-in `User` model for ownership.
- [x] Reference `Product` with an explicit deletion policy, using `PROTECT` unless a concrete later requirement changes it.
- [x] Add a positive integer `quantity` field with a maximum of 99 as a defensive constraint.
- [x] Add a database uniqueness constraint for `(user, product)` so each user has at most one row per product.
- [x] Define stable cart-item ordering for display.
- [x] Generate and inspect the migration for only the intended cart schema and constraints.
- [x] Apply the migration against the ignored local SQLite database.

## Quantity Form and Add Flow

- [x] Add a quantity form for the product detail page.
- [x] Require an integer quantity from 1 through 99.
- [x] Render a CSRF token and visible validation errors in the product detail template.
- [x] Add a named authenticated POST route for adding the selected product to the current user's cart.
- [x] Resolve the product from the URL with `get_object_or_404`.
- [x] Derive cart ownership from `request.user`; do not accept a user ID from submitted data.
- [x] Create a cart row with the submitted quantity when the user has no existing row.
- [x] Increment an existing row by the submitted quantity rather than replacing it.
- [x] Use an atomic transaction and safe update strategy for repeated additions.
- [x] Reject invalid, missing, zero, negative, decimal, non-numeric, and greater-than-99 quantities without modifying the cart.
- [x] Redirect successful additions to the prefix-aware cart page and preserve the Coderange URL-prefix behavior.
- [x] Ensure GET requests never mutate cart state.

## Cart Page and Templates

- [x] Add a named authenticated `/cart/` view.
- [x] Query only the current user's `CartItem` rows.
- [x] Display each item's product name, unit price, quantity, and line total.
- [x] Display a clear empty-cart state when the current user has no items.
- [x] Add a prefix-aware cart link to the product detail page and any other appropriate authenticated navigation.
- [x] Keep checkout controls and cart update/remove controls out of this feature.
- [x] Use Django URL reversing for every application link; do not hard-code `/proxy/8000`.

## Tests

- [x] Add model tests for cart ownership, quantity validation, uniqueness, and product deletion behavior.
- [x] Test authenticated product detail form rendering, including quantity bounds and CSRF token presence.
- [x] Test a valid add-to-cart POST creates the correct row and quantity.
- [x] Test a repeated add increments the existing row without creating a duplicate.
- [x] Test invalid quantities produce visible errors and no database write.
- [x] Test GET requests do not add or change cart items.
- [x] Test the cart page displays only the logged-in user's items, including line totals and empty state.
- [x] Test two users cannot see or mutate each other's cart rows.
- [x] Test anonymous detail, add, and cart requests redirect to the prefix-aware login URL.
- [x] Test successful add redirects to the prefix-aware cart URL.
- [x] Test URL reversing and rendered form/cart links with `/proxy/8000` and with an empty local prefix.
- [x] Preserve all existing authentication and product browsing tests.

## Verification and Documentation

- [x] Run `python manage.py makemigrations core` and inspect the generated migration.
- [x] Run `python manage.py migrate --noinput`.
- [x] Run `python manage.py check` with the proxy prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [x] Load the existing product fixture for manual verification.
- [x] Create or use an authenticated user and add a sample product with a quantity between 1 and 99.
- [ ] Confirm the cart page shows the expected product, unit price, quantity, and line total. Blocked in this shell because no authenticated browser session is available.
- [ ] Submit the add form through the Coderange forwarded URL and confirm CSRF validation succeeds. Requires external UI verification.
- [x] Inspect the diff for credentials, local databases, virtual-environment files, user-specific cart fixtures, and unrelated changes.
- [x] Commit implementation changes with a Conventional Commit message such as `feat: add shopping cart`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the feature branch, tests, migration, and commit history before rendezvous.
- [ ] Merge the cart branch into `main` without overwriting unrelated changes.
- [ ] Re-run migrations, Django checks, the full test suite, and forwarded-URL smoke verification on merged `main`.
- [ ] Confirm the merged application starts and serves the authenticated add-to-cart and cart display flow.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the cart model, routes, quantity policy, prefix behavior, manual verification commands, and current feature state.
