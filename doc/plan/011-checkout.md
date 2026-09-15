# Checkout Plan

## Branch and Scope

- [x] Confirm the working tree and preserve any unrelated user changes before implementation.
- [x] Create a focused checkout feature branch from current `main`.
- [x] Keep this feature limited to editable checkout, purchase transaction persistence, line-item snapshots, cart clearing, and focused tests.
- [x] Do not implement payment processing, shipping, taxes, discounts, inventory reservation, guest checkout, refunds, cancellation, product administration, or transaction history UI.

## Purchase Models and Migration

- [x] Add a `Transaction` model with authenticated user, creation timestamp, and non-negative decimal total.
- [x] Add a `TransactionLineItem` model linked to `Transaction`.
- [x] Store a nullable product reference with an explicit deletion policy that preserves historical transactions.
- [x] Store an immutable product-name snapshot on every line item.
- [x] Store an immutable unit-price decimal snapshot on every line item.
- [x] Store a positive quantity on every line item with the existing maximum of 99 per product.
- [x] Add database constraints for non-negative totals and positive quantities.
- [x] Generate and inspect the migration for only the intended transaction schema and constraints.
- [x] Apply the migration against the ignored local SQLite database.

## Checkout Forms and Routes

- [x] Add an authenticated checkout page at `/checkout/`.
- [x] Add a checkout form that renders current user cart rows with editable quantities from 1 through 99.
- [x] Add a clear remove action for individual cart rows on the checkout page.
- [x] Distinguish update, remove, and complete-purchase POST actions without trusting submitted user IDs, prices, or totals.
- [x] Validate all submitted quantities before mutating cart state.
- [x] Filter every cart lookup and mutation by `request.user`.
- [x] Use CSRF protection for every checkout mutation form.
- [x] Re-read cart rows, products, and prices from the database on final purchase submission.
- [x] Add a clear confirmation response or page after successful purchase.
- [x] Use `redirect_without_script_prefix()` for update, remove, completion, and confirmation redirects.
- [x] Use Django URL reversing for checkout form actions and links so regular HTML paths include `/proxy/8000` when configured.
- [x] Keep `/cart/` as the existing overview page and add an appropriate checkout link.

## Checkout Transaction

- [x] Wrap final transaction creation, line-item creation, and cart deletion in one `transaction.atomic()` block.
- [x] Reject checkout when no current cart rows remain and avoid creating an empty transaction.
- [x] Calculate every line total from server-side decimal price snapshots and submitted/validated quantities.
- [x] Calculate and persist the transaction total from the line items, never from client-submitted totals.
- [x] Create one line item per current cart row.
- [x] Snapshot product name and unit price before any later product mutation can affect history.
- [x] Clear only the current user's cart after all transaction records are successfully created.
- [x] Define and test behavior for repeated checkout submission using POST/redirect/GET and the minimum acceptable duplicate-submission protection.

## Templates

- [x] Add a project-owned checkout template with product name, unit price, quantity controls, line totals, remove controls, and order total.
- [x] Show a clear empty-cart/empty-checkout state.
- [x] Show validation errors without applying invalid quantity changes.
- [x] Add checkout navigation from the existing cart page.
- [x] Render purchase confirmation details without exposing another user's transaction data.

## Tests

- [x] Add model tests for transaction totals, line-item snapshots, quantity constraints, and product deletion behavior.
- [x] Test authenticated checkout page access and rendering.
- [x] Test quantity updates for valid values 1 and 99.
- [x] Test invalid, missing, zero, negative, decimal, and above-99 quantities do not mutate the cart.
- [x] Test removing one item leaves other cart items unchanged.
- [x] Test user isolation for checkout display, updates, removals, and completion.
- [x] Test successful checkout creates one transaction with correct line items and total.
- [x] Test line items preserve product name and price after the product is changed.
- [x] Test line items remain readable after the referenced product is deleted according to the selected deletion policy.
- [x] Test successful checkout clears only the current user's cart.
- [x] Test empty checkout does not create a transaction.
- [x] Test transaction creation failure rolls back line items and cart deletion.
- [x] Test submitted prices and totals cannot alter the server-calculated purchase.
- [x] Test anonymous checkout and mutation requests redirect to the prefix-aware login flow.
- [x] Test regular checkout links/forms include `/proxy/8000` while source redirect locations remain unprefixed.
- [x] Preserve all existing authentication, product browsing, cart, and redirect-prefix tests.

## Verification and Documentation

- [x] Run `python manage.py makemigrations core` and inspect the generated migration.
- [x] Run `python manage.py migrate --noinput`.
- [x] Run `python manage.py check` with the proxy prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [x] Load the product fixture for manual verification.
- [ ] Create a user cart, adjust quantities, remove an item, and complete a purchase through the local flow. Automated flow coverage passes; interactive browser verification remains.
- [x] Confirm the transaction total, line items, snapshots, and cleared cart in the database/application.
- [ ] Verify the Coderange UI checkout flow, CSRF validation, and final redirect prefix. Requires live UI verification.
- [x] Inspect the diff for credentials, databases, virtual environments, user-specific fixtures, and unrelated changes.
- [x] Commit implementation changes with a Conventional Commit message such as `feat: add checkout`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the checkout branch, migration, tests, and commit history.
- [ ] Merge the checkout branch into `main` without overwriting unrelated changes.
- [ ] Re-run migrations, checks, the full test suite, and Coderange checkout smoke verification on merged `main`.
- [ ] Confirm the merged application starts and completes purchases while clearing the current user's cart.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with checkout routes, editable-cart behavior, transaction snapshot policy, cart-clearing behavior, redirect-prefix rules, and verification commands.
