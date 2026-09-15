# Product Browsing Study

## Scope

Feature 2 adds the coffee product catalog experience:

- Store products with a name and price.
- Show products on the authenticated home page in a table.
- Let a user click a product to open a detail page showing its name and price.

The existing authentication boundary remains in force. Anonymous users must still be redirected to `/login/` before they can view the home page or a product detail page. This feature does not include cart operations, checkout, purchases, transaction history, product administration, product images, categories, search, filtering, or product creation UI.

## Current Codebase

The Django project is `digitalcafe` with the registered `core` app. Django's built-in authentication is already implemented and merged into `main`. The root view in `core/views.py` is protected with `login_required` and currently renders a greeting-only template. The root URL is `/`, login is at `/login/`, and no application models or product routes exist yet. The built-in admin is enabled, but product administration is intentionally a later feature.

The working tree is clean on `main` and synchronized with `origin/main`. The existing development settings include the coderange forwarding host and trusted CSRF origin; product browsing should not alter those settings unnecessarily.

## Feasibility

This feature is a direct fit for Django's ORM, template rendering, URL routing, and built-in authentication. A `Product` model in `core` can represent the catalog with a required name and a currency-safe decimal price. A migration will create the SQLite table. Function-based, authenticated views can query products, render the home table, and use `get_object_or_404` for a product detail page.

The product detail URL should use the product's integer primary key for now. It is stable, requires no extra slug field, and avoids introducing URL and uniqueness policy that the request does not need. A later feature can add slugs if human-readable or externally shared URLs become a requirement.

## Proposed Approach

1. Add a `Product` model to `core.models` with:
   - a non-blank, bounded `name` field;
   - a non-negative `DecimalField` price with two decimal places and a suitable maximum digit count;
   - a deterministic ordering, preferably by name and then primary key, so the catalog does not depend on database insertion order.
2. Create and apply a Django migration for the model using the existing SQLite database.
3. Replace the greeting-only home behavior with an authenticated product-list view that queries all products in the defined order and passes them to the home template.
4. Preserve the existing logged-in greeting above the product table so Feature 1 behavior remains visible while the home page gains catalog content.
5. Render a table with product name, price, and a link from each product name to its detail page.
6. Add an authenticated product detail view at `/products/<int:pk>/`, retrieving the product or returning HTTP 404 when it does not exist.
7. Render the detail page with the product name and price, plus a link back to the home catalog. Do not add cart controls until the cart feature is planned.
8. Add a small, explicit sample-product fixture for manual verification. Load it with Django's `loaddata` command after migrations rather than seeding records automatically in application code or adding an unrequested product-management interface.
9. Add focused model, view, URL, authentication, ordering, and template tests. Create test products directly in tests so the test suite remains isolated from the optional manual-verification fixture.

The built-in admin can remain unchanged for this feature. The model will be available to admin only after the later product administration feature explicitly registers and configures it.

## Tradeoffs

- A `DecimalField` is necessary for monetary values; using a float would introduce rounding errors in prices and future transaction totals.
- Keeping the price at two decimal places matches ordinary currency display while allowing later cart and transaction features to reuse the stored value.
- Integer primary-key URLs are the smallest correct design. Slugs would improve readability but add a field, uniqueness rules, migration considerations, and edit behavior without being requested.
- A single `Product` model in the existing `core` app avoids premature app fragmentation. If the catalog grows substantially, extraction into a dedicated app can be planned later.
- The home page will continue to greet the user and add the catalog below it, preserving the completed authentication behavior while making `/` the product entry point.
- An explicit fixture is preferable to a data migration for sample products: it lets developers opt into demo data with `loaddata`, avoids inserting demo products into every environment during deployment, and can be omitted from production workflows. Empty-catalog behavior should still be explicit and testable, while later admin work can provide the operational path for managing products.
- Querying all products is appropriate for the requested simple shop. Pagination, search, filtering, and availability fields should wait until the catalog requirements justify them.

## Risks and Mitigations

- A product detail view without authentication would violate the application-wide access requirement. Mitigation: apply `login_required` to the detail view and test anonymous access.
- A missing product should not produce an unhandled exception. Mitigation: use `get_object_or_404` and test the HTTP 404 response for an unknown primary key.
- Prices may render inconsistently if templates rely on implicit formatting. Mitigation: use Django's decimal and localization-safe display approach consistently in both list and detail templates, and test the visible value.
- Product names may contain HTML-sensitive input. Mitigation: rely on Django template auto-escaping and test rendered content through the template response rather than marking values safe.
- Existing authentication tests assert the greeting on `/`. Mitigation: retain that greeting and extend, rather than replace, the existing home-page test coverage.
- An empty database is expected before products are created. Mitigation: render a clear empty-catalog message and cover it with a test. Provide an optional fixture and document `loaddata` so manual verification can populate representative products without runtime seeding.
- Future cart and transaction features need stable product prices. Mitigation: store prices as decimals now; later transaction line items must snapshot the price at purchase time in their own planned feature.

## Verification Strategy

- Run `python manage.py makemigrations core` and inspect the generated migration.
- Run `python manage.py migrate --noinput` against the ignored local SQLite database.
- Run `python manage.py check`.
- Run the full Django test suite, including:
  - authenticated home access and retained username greeting;
  - product rows displaying names and prices;
  - deterministic product ordering;
  - product-name links resolving to the correct detail URL;
  - detail page displaying the selected product's name and price;
  - unknown product IDs returning HTTP 404;
  - anonymous requests to both catalog and detail pages redirecting to login.
- Start the development server and manually confirm the authenticated home table and product detail navigation.
- Load the committed sample fixture with `python manage.py loaddata products` and manually confirm representative products appear in the authenticated home table and detail navigation.
- Confirm no local SQLite database, virtual-environment files, credentials, or unrelated settings changes are included in the feature commit.

## Open Decisions for the Plan

- Use `name`, `price`, and the generated integer primary key as the complete initial product schema.
- Use `/products/<int:pk>/` for product details.
- Display prices with two decimal places and no product currency conversion logic.
- Keep product creation and editing out of this feature; the later admin feature will define that workflow.
- Use an optional `core/fixtures/products.json` fixture with a few representative coffee products for manual verification; do not load it automatically.
