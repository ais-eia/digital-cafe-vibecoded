# Transaction History Plan

## Branch and Scope

- [x] Confirm the working tree and preserve unrelated user changes before implementation.
- [x] Create a focused transaction-history branch from current `main`.
- [x] Keep this feature read-only and limited to authenticated history display.
- [x] Do not add admin reporting, refunds, cancellation, editing, exports, search, filtering, pagination, or payment-provider data.
- [x] Do not change checkout transaction creation or line-item snapshot behavior except where tests expose a concrete regression.

## History View and URL

- [x] Add an authenticated transaction-history view at `/transactions/`.
- [x] Query only `Transaction` rows belonging to `request.user`.
- [x] Preserve newest-first ordering from the transaction model.
- [x] Use `prefetch_related('line_items')` to load line items efficiently.
- [x] Add a named URL for the history view without hardcoding `/proxy/8000`.
- [x] Add a prefix-aware history link from the purchase confirmation page.
- [x] Keep the history page read-only with no mutation forms or delete actions.

## History Template

- [x] Add a project-owned transaction history template.
- [x] Render a clear empty-history message such as `No purchases yet.`.
- [x] Render each transaction's identifier, creation timestamp, and stored total.
- [x] Render every line item's stored `product_name`, `unit_price`, quantity, and calculated snapshot line total.
- [x] Use the stored snapshot fields for all user-facing product names and prices; do not render current `Product.name` or `Product.price`.
- [x] Make the template readable when a line item's nullable product reference is `NULL`.
- [x] Preserve escaped output for snapshot product names.

## Explicit Snapshot Regression Test

- [x] Create a transaction with a line item snapshot such as product name `House Blend` and unit price `3.50`.
- [x] Change the associated product's name and price after the transaction exists, for example to `Renamed Coffee` and `9.99`.
- [x] Request the rendered `/transactions/` page as the transaction owner.
- [x] Assert the response contains the original snapshot name `House Blend` and original snapshot price `$3.50`.
- [x] Assert the response does not contain the current product name `Renamed Coffee` or current product price `$9.99` for that line item.
- [x] Delete the associated product, request the rendered history page again, and assert the original snapshot name and price still appear.
- [x] Assert the history page remains readable after the product foreign key becomes `NULL`.

## Tests

- [x] Test an authenticated user with no transactions sees the empty state.
- [x] Test a user with multiple transactions sees newest-first ordering, identifiers, timestamps, totals, and all line items.
- [x] Test transaction history excludes every other user's transactions and line items.
- [x] Test the explicit post-purchase product rename/price-change snapshot assertions against rendered page content.
- [x] Test the explicit post-purchase product deletion snapshot assertions against rendered page content.
- [x] Test anonymous access redirects to the correct login URL and `next` value.
- [x] Test the generated history link includes `/proxy/8000/transactions/` with the Coderange prefix configured.
- [x] Preserve all existing authentication, product, cart, checkout, and redirect-prefix tests.

## Verification and Documentation

- [x] Run `python manage.py check` with the proxy prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [x] Load the product fixture and complete at least one purchase for manual history verification.
- [ ] Change and delete a purchased product, then manually confirm the history page still displays its original name and price snapshots. Automated rendered-page assertions pass; interactive browser verification remains.
- [ ] Verify the Coderange UI history link and page remain under `/proxy/8000/`. Requires live UI verification.
- [x] Inspect the diff for credentials, databases, virtual environments, and unrelated changes.
- [x] Commit implementation with a Conventional Commit message such as `feat: add transaction history`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the history branch, tests, and commit history.
- [ ] Merge the transaction-history branch into `main` without overwriting unrelated changes.
- [ ] Re-run checks, the full test suite, and Coderange history smoke verification on merged `main`.
- [ ] Confirm the merged application starts and displays only the current user's transaction history.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the history route, user isolation, snapshot rendering policy, and verification commands.
