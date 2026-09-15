# Checkout Study

## Scope

Feature 4 turns the current persistent cart into a checkout flow:

- Authenticated users can view a checkout page containing their cart items.
- Users can change each item's quantity or remove an item directly on that page.
- Users can submit the checkout to complete a purchase.
- Completing a purchase records a transaction with line items and clears the user's cart.

This feature does not include payment processing, shipping, taxes, discounts, inventory reservation, guest checkout, refunds, cancellation, product administration, or transaction history UI. Transaction history is a later feature, although the transaction data created here must support it.

## Current Codebase

The Django `core` app currently has `Product` and user-owned `CartItem` models. Cart quantities are positive integers from 1 through 99, with one cart row per user/product. Product prices are decimal values. The authenticated `/cart/` page is read-only and displays current products, unit prices, quantities, and line totals. Product detail POST adds to the cart and uses `redirect_without_script_prefix()` so Coderange prefixes the response exactly once.

The application uses SQLite, Django migrations, built-in authentication, CSRF middleware, and an environment-backed `FORCE_SCRIPT_NAME` for regular HTML URL generation. Application redirects must use the unprefixed redirect helper because Coderange automatically prefixes redirect `Location` headers.

## Feasibility

Django's ORM can model durable purchases with a transaction header and line items. A `Transaction` model can belong to a user and record creation time and a total. A `TransactionLineItem` model can belong to a transaction and snapshot the purchased product name, unit price, and quantity. The line item should retain its own values so later product edits or deletions cannot change historical purchase records.

The checkout submission should be one atomic database operation: validate the submitted cart changes, create the transaction and all line items using one consistent price snapshot, delete the user's cart rows, and commit. If any step fails, neither the purchase nor cart changes should be partially persisted.

## Proposed Approach

1. Add purchase models:
   - `Transaction`: user, created timestamp, and total amount.
   - `TransactionLineItem`: transaction, product reference if useful for reporting, product-name snapshot, unit-price snapshot, and quantity.
   - Add constraints for positive quantities and non-negative monetary values.
2. Add a checkout form that represents the editable cart in one POST. Each current cart row should have a quantity field from 1 through 99 and a remove control. The form must identify cart rows with server-rendered IDs but must derive ownership from `request.user`.
3. Add an authenticated checkout page, likely `/checkout/`, listing product name, current unit price, editable quantity, line total, remove control, and order total.
4. Support a clear POST action distinction, such as a row-specific `remove_item` value or an action field. Quantity updates should be validated before any writes. Removing an item should delete only that user's row.
5. Provide a separate checkout-submit action from the checkout page. On submission, re-read the current user's cart and product prices inside an atomic transaction, create a transaction and line items, calculate the total from the server-side decimal prices, delete the cart, and redirect to a purchase confirmation page or checkout-complete response.
6. Use `redirect_without_script_prefix()` for successful update, remove, checkout-submit, and confirmation redirects. Keep regular checkout form actions and links generated with `{% url %}` so they include `/proxy/8000` in HTML.
7. Add tests for cart editing, removal, user isolation, checkout atomicity, line-item snapshots, cart clearing, total calculation, empty-cart submission, and prefix-aware links/redirects.

The existing `/cart/` page can either become the editable checkout page or remain a read-only cart page with a checkout link. The requested wording says “checkout page,” so the preferred design is to add `/checkout/` and preserve `/cart/` as a simple cart overview/navigation page, unless the implementation plan chooses to consolidate them explicitly.

## Data and Price Policy

- Cart edits use the existing 1-to-99 quantity policy.
- A remove action deletes the selected cart row and does not create a transaction.
- Checkout prices must be read from the database at submission time, not trusted from hidden form fields.
- Each transaction line item snapshots the product name and unit price used for the purchase.
- The transaction total is calculated server-side as the sum of line-item unit price multiplied by quantity.
- A checkout with no remaining cart items must not create an empty transaction; it should return a clear empty-cart/checkout message.
- The cart is cleared only after transaction and line-item creation succeeds inside the same database transaction.
- Product foreign-key behavior for historical lines should preserve history. A nullable `SET_NULL` reference plus snapshots is safer than `PROTECT` if future admin work needs to remove products; the exact deletion policy should be finalized in the plan.

## Tradeoffs

- Separate transaction and line-item tables are more work than a single JSON snapshot, but they support reporting, history, integrity checks, and future transaction-history UI.
- Keeping a nullable product reference alongside snapshots allows historical records to survive product deletion while retaining an optional link to the current product.
- Re-reading prices at final submission prevents clients from tampering with prices, but a price could change between viewing checkout and submitting. The snapshot records the authoritative submission-time price; a later pricing-lock feature can add a different business rule.
- A single combined checkout form simplifies the page but requires careful parsing and validation of multiple row controls. Per-row update/remove forms are easier to reason about but can cause more page reloads. A combined form with explicit action values is acceptable for this simple app.
- Checkout and cart edits should be POST-only with CSRF protection. This avoids accidental mutation through links or crawlers.
- SQLite supports the required atomic transaction for this local application. Production concurrency and database isolation may require further deployment planning.
- No payment gateway or external service is needed for recording the requested local purchase.

## Risks and Mitigations

- A client could submit another user's cart-item ID. Mitigation: filter every lookup and mutation by `request.user`.
- A client could tamper with product prices or totals. Mitigation: ignore submitted prices/totals and calculate from current database values.
- Partial transaction creation could leave a purchase and cart in inconsistent states. Mitigation: wrap transaction, line creation, and cart deletion in `transaction.atomic()`.
- A cart could change between edit and checkout submission. Mitigation: re-query cart rows during finalization and define behavior for an empty or changed cart; tests should cover current server state.
- Duplicate checkout submissions could create duplicate purchases. Mitigation: use POST/redirect/get and consider an idempotency token or disable repeated submission if the UI requires stronger protection. The initial plan should explicitly decide the minimum protection needed.
- Historical line items could change when products are edited or deleted. Mitigation: snapshot name and price on each line and choose an explicit nullable product reference policy.
- Quantity values above 99 or invalid values could bypass form validation. Mitigation: validate both forms and model/database constraints.
- Coderange could double-prefix checkout redirects if ordinary `redirect()` is used. Mitigation: use the established unprefixed redirect helper for every application redirect.
- An empty cart could produce an empty transaction. Mitigation: reject finalization when no valid cart rows remain and display a clear message.

## Verification Strategy

- Run `python manage.py makemigrations core` and inspect the transaction schema migration.
- Run `python manage.py migrate --noinput`.
- Run `python manage.py check` with the proxy prefix unset and configured.
- Test checkout page access and rendering for authenticated users.
- Test quantity changes from the checkout page, including values 1, 99, invalid values, and above 99.
- Test removing one item leaves other items untouched.
- Test user isolation for editing and removing cart rows.
- Test successful checkout creates one transaction, correct line items, snapshots names/prices, calculates the total, and clears the cart.
- Test checkout uses database prices rather than submitted hidden values.
- Test empty checkout does not create a transaction.
- Test a transaction failure rolls back line items and cart deletion.
- Test anonymous checkout and mutation requests redirect correctly.
- Test regular checkout links/forms include `/proxy/8000` while redirect `Location` values remain unprefixed at Django's source.
- Load the product fixture, create a user/cart, manually edit quantities, remove an item, and complete a purchase through the Coderange UI.
- Confirm the final live redirect is prefixed exactly once and the cart is empty after completion.
