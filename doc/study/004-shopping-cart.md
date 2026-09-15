# Shopping Cart Study

## Scope

Feature 3 adds a persistent personal cart for authenticated users:

- A logged-in user can add a product from its detail page.
- The user specifies a quantity when adding the product.
- Cart contents belong to that user and must not be visible across accounts.
- Adding the same product again should have defined, tested behavior.

This feature does not include checkout submission, purchases, transaction records, transaction line items, payment processing, cart history, product administration, guest carts, or inventory management. The existing authentication and proxy-prefix behavior remain required.

## Current Codebase

The Django project uses the `core` app and the built-in `User` model. Products are stored in `core.Product`, with decimal prices and authenticated detail pages at `/products/<id>/`. The product detail template currently displays the product and a back-to-menu link but has no form. All application pages are protected with `login_required`. URL generation is configured with `DJANGO_SCRIPT_NAME`, defaulting to `/proxy/8000` for Coderange and supporting an empty value for direct local development.

The database is SQLite, migrations are committed, and tests use Django's isolated test database. There is no cart model, cart URL, or cart template yet.

## Feasibility

Django's ORM is well suited to a user-owned cart. A normalized `CartItem` model can associate one `User` and one `Product` with a positive integer quantity. A database uniqueness constraint on `(user, product)` prevents duplicate rows and allows repeated additions to increment an existing line. This design persists carts across sessions and devices for the same user and is ready for the later checkout feature.

A server-side POST form on the authenticated product detail page is preferable to a session-only or client-side cart. It keeps ownership and quantities authoritative on the server, works with the existing CSRF protection, and lets the later checkout feature query exactly what the user currently owns.

## Proposed Approach

1. Add a `CartItem` model with:
   - a foreign key to Django's built-in `User` model;
   - a foreign key to `Product`;
   - a positive integer `quantity`;
   - a uniqueness constraint for one row per user/product pair;
   - useful ordering for stable cart display, such as product name and primary key.
2. Create and apply a migration for the cart table and constraint.
3. Add a quantity form to the product detail page. Use a positive integer field, require a submitted quantity, and show validation errors without modifying the cart when the value is invalid.
4. Add an authenticated POST endpoint for adding a product to the current user's cart. Use `get_object_or_404` for the product, validate the quantity, create a new cart item, or increment the existing item atomically.
5. Add an authenticated cart page, likely `/cart/`, listing the current user's items, product names, quantities, unit prices, and line totals. Keep checkout controls out of this feature unless the implementation needs a navigation placeholder.
6. Add a cart link from the authenticated product detail and/or home pages using Django URL reversing so the Coderange prefix remains correct.
7. Add tests for successful additions, repeated additions, invalid and missing quantities, user isolation, anonymous redirects, cart display, and prefix-aware URLs.

The cart should use POST for mutation and include `{% csrf_token %}`. The form must not accept a user identifier from the browser; ownership comes from `request.user`. Product price should be read from the current product for display only. The later checkout feature must decide how to snapshot prices in transaction line items.

## Quantity and Repeated-Add Policy

The initial policy should be explicit:

- Quantity must be an integer greater than or equal to 1.
- A quantity of zero, a negative value, a decimal, missing input, or non-numeric input is rejected with a visible validation error.
- Adding a product not currently in the user's cart creates a row with the submitted quantity.
- Adding a product already in the user's cart increments its quantity by the submitted amount rather than replacing it.
- Enforce a maximum quantity of 99 at the form/model boundary as a confirmed defensive constraint. This is not an inventory rule; it limits accidental or abusive submissions while a later business requirement can revise the value.

This additive behavior is intuitive for an “add to cart” action and avoids silently discarding a quantity selected earlier. A later cart-management feature can add explicit update and remove operations.

## Tradeoffs

- A normalized database cart is more durable and queryable than a session dictionary, but it requires a migration and cleanup behavior for deleted products.
- Keeping `Product` as a foreign key preserves referential integrity. The implementation should choose `PROTECT` or another explicit deletion policy so a product used by a cart is not silently removed; product administration is a later feature and should not erase a user's pending cart unexpectedly.
- One row per user/product with a uniqueness constraint simplifies display and checkout compared with allowing duplicate cart lines.
- Incrementing existing quantities is convenient, but concurrent adds can lose updates without an atomic transaction and database expression. Use `transaction.atomic()` plus an `F()` expression or a safe locked update strategy.
- A simple server-rendered form avoids JavaScript and dependencies. It may require a full page reload, which is acceptable for the current minimal application.
- A cart page is included because users need a way to inspect what was added, but cart update/remove controls are deferred to keep this feature narrowly scoped.
- No sample cart fixture should be committed because cart data is user-specific and depends on database user/product identities.

## Risks and Mitigations

- A cart endpoint that trusts a submitted user ID could allow cross-account writes. Mitigation: derive ownership exclusively from `request.user` and test two users with the same product.
- A GET mutation could be triggered by crawlers or accidental link visits. Mitigation: require POST and test that GET does not add an item.
- Missing CSRF protection would expose cart mutations. Mitigation: render a CSRF token, preserve Django's CSRF middleware, and test the normal form submission path.
- Negative, zero, quantities above 99, or malformed quantities could create invalid or abusive cart rows. Mitigation: validate positive integers, enforce the confirmed maximum of 99, and add model/form tests.
- Two simultaneous additions could overwrite each other. Mitigation: use an atomic database update and test the resulting increment logic as far as SQLite's test environment permits.
- A product could be deleted while a cart item references it. Mitigation: select an explicit foreign-key deletion policy and document it for the later admin feature.
- The proxy prefix could be lost in form actions or cart links. Mitigation: use named `{% url %}` tags, prefix-aware reverse assertions, and UI verification through `/proxy/8000/`.
- Future checkout totals must not trust a mutable current product price. Mitigation: treat cart prices as current display values and require the checkout study to define immutable transaction-line price snapshots.

## Verification Strategy

- Run `python manage.py makemigrations core` and inspect the migration.
- Run `python manage.py migrate --noinput`.
- Run `python manage.py check` with the proxy prefix unset and configured.
- Run tests covering:
  - authenticated product detail form rendering;
  - valid add-to-cart POST and quantity persistence;
  - repeated add increments rather than duplicates;
  - invalid quantities rejected without writes;
  - GET requests do not mutate the cart;
  - cart page displays only the current user's items;
  - anonymous access redirects to login;
  - users cannot see or mutate another user's cart;
  - prefix-aware form actions, cart links, and redirects.
- Load the existing product fixture for manual verification, create or use an authenticated user, add a product with several quantities, and confirm the cart page shows the expected quantity and line information.
- Submit the form through the Coderange forwarded URL and confirm CSRF validation succeeds.
- Confirm no local database, virtual environment, credentials, or user-specific cart fixture is committed.

## Open Decisions for the Plan

- Use a `CartItem` model rather than session-only storage.
- Use `/cart/` for the authenticated cart page and a named POST add route, with exact route names finalized in the plan.
- Use a positive integer quantity with a maximum of 99 per product as a defensive constraint, not an inventory rule.
- Increment existing quantities on repeated add operations.
- Use `PROTECT` for the product foreign key unless product administration requirements establish a different deletion policy.
- Defer cart update/remove controls, checkout, transaction recording, payments, and inventory checks.
