# Transaction History Study

## Scope

Feature 5 lets an authenticated user view their past purchases. The history should list transactions belonging to the current user and expose enough information to understand each purchase, including its date, total, and line items.

This feature does not include admin reporting, cross-user access, refunds, cancellation, editing historical records, exports, search, filtering, pagination, or payment-provider data. Existing transaction creation and checkout behavior must remain unchanged.

## Current Codebase

The `core` app now stores `Transaction` records with a user, `created_at`, and total. Each `TransactionLineItem` belongs to a transaction and stores a nullable product reference plus immutable `product_name`, `unit_price`, and quantity snapshots. This preserves purchase history if a product is renamed, repriced, or deleted. `Transaction` orders newest first, and line items order by primary key.

Checkout creates transactions atomically, clears the current user's cart, and redirects to an owner-protected confirmation page at `/checkout/complete/<id>/`. There is no transaction-history route or template. URL generation uses the Coderange script prefix for HTML links and `redirect_without_script_prefix()` for application redirects.

## Feasibility

The existing transaction schema directly supports a read-only history page. A login-protected list view can query `Transaction.objects.filter(user=request.user)` with prefetched line items and render the snapshot fields. No migration is required unless the implementation chooses an additional display field or index.

A single history page at `/transactions/` is sufficient for the requested feature. Each transaction can be displayed as a section or table containing its ID, creation timestamp, total, and line items. A separate detail route is not required by the request, but a named transaction detail page may make the history easier to read and extend. The implementation plan should choose the smallest useful presentation while ensuring line items are visible.

## Proposed Approach

1. Add an authenticated transaction-history view at `/transactions/`.
2. Query only the current user's transactions, newest first, with `prefetch_related('line_items')` to avoid one database query per transaction.
3. Render each transaction's creation time, total, identifier, and line items using `product_name`, `unit_price`, quantity, and line total from the stored snapshot fields.
4. Add a prefix-aware navigation link to the history page from the authenticated confirmation page and an appropriate shared page such as the cart or home page.
5. Keep the page read-only. Do not allow users to modify or delete transactions.
6. Add tests for authentication, user isolation, ordering, snapshot display after product changes/deletion, totals, line items, and prefix-aware URL generation.

The preferred initial design is a single `/transactions/` page with all line items inline. A separate detail route can be added later if history grows or pagination becomes necessary.

## Data Integrity and Privacy

- Filter transactions by `request.user` in the database query.
- Do not accept a user ID or expose another user's transaction identifier as an authorization mechanism.
- Use stored transaction totals and line-item snapshots, never current product prices, for historical display.
- Display the nullable product reference only as an internal relation if needed; the user-facing name must come from `product_name`.
- Preserve the transaction's stored timestamp and order; do not derive purchase dates from mutable product data.
- Do not add mutation endpoints to history.

## Tradeoffs

- Inline line items minimize routes and clicks and directly satisfy the request, while a detail page would be more extensible but adds unnecessary surface area now.
- `prefetch_related` keeps the simple template efficient without introducing denormalized history data.
- Showing transaction IDs helps users distinguish purchases, but the initial UI can remain minimal and use the created timestamp as the primary visual identifier.
- No pagination is needed for a simple local coffee shop history, but the query and template should be structured so pagination can be added later.
- No new model fields or migration are needed because the checkout feature already created the required durable snapshots.

## Risks and Mitigations

- A missing user filter could expose all customers' purchases. Mitigation: filter by `request.user` and test multiple users.
- Reading live `Product` values could make old purchases inaccurate. Mitigation: render line-item snapshots and test after renaming, repricing, and deleting products.
- N+1 queries could grow with transaction count. Mitigation: use `prefetch_related('line_items')` and keep query behavior testable where practical.
- A history link could be inaccessible under Coderange if hardcoded. Mitigation: use `{% url %}` and test the generated `/proxy/8000/transactions/` path.
- An anonymous user could access the route without authentication. Mitigation: apply `login_required` and test the prefix-aware login redirect.
- Empty history may be confusing. Mitigation: render a clear message such as “No purchases yet.”

## Verification Strategy

- Run `python manage.py check` with both prefix configurations.
- Run the full Django test suite.
- Test an authenticated user with no transactions sees the empty state.
- Test a user with multiple transactions sees newest first, totals, timestamps, and all line items.
- Test a user cannot see another user's transactions.
- Test historical names and prices remain correct after product updates and deletion.
- Test anonymous history access redirects to the correct login flow.
- Test generated history links include `/proxy/8000` in HTML while no history mutation redirects are introduced.
- Load products, complete purchases through checkout, and manually verify history through the Coderange UI.
