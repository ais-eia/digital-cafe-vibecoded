# Product Browsing Plan

## Branch and Scope

- [x] Confirm the working tree and preserve any unrelated user changes before implementation.
- [x] Create a focused feature branch from the current `main` branch.
- [x] Keep this feature limited to the product model, authenticated catalog table, authenticated product detail page, and focused tests.
- [x] Do not implement cart operations, checkout, transactions, transaction history, product administration, registration, search, filtering, categories, or images. The only data setup included is an optional sample-product fixture for manual verification.

## Product Model and Migration

- [x] Add a `Product` model to `core.models`.
- [x] Add a required bounded `name` field.
- [x] Add a non-negative `DecimalField` price with two decimal places and an appropriate maximum digit count.
- [x] Define deterministic model ordering by product name and primary key.
- [x] Generate the `core` migration and inspect it for the intended schema only.
- [x] Apply migrations against the ignored local SQLite database.
- [x] Add `core/fixtures/products.json` with a small set of representative coffee products and valid decimal prices.
- [x] Keep the fixture optional; do not load sample products automatically through a data migration or application startup code.

## Catalog and Detail Views

- [x] Update the authenticated home view to query all products in deterministic order.
- [x] Preserve the existing logged-in username greeting on the home page.
- [x] Add a product table showing each product's name and two-decimal price.
- [x] Link each product name to its detail URL.
- [x] Render a clear empty-catalog message when no products exist.
- [x] Add an authenticated product detail view at `/products/<int:pk>/`.
- [x] Retrieve detail records with `get_object_or_404`.
- [x] Render the detail page with product name, price, and a link back to the catalog.
- [x] Keep cart controls out of the detail page until the cart feature is planned.
- [x] Leave the built-in admin registration unchanged for the later product administration feature.

## Templates and URLs

- [x] Extend the existing home template without removing the Feature 1 greeting.
- [x] Add a project-owned product detail template under the `core` app templates.
- [x] Use Django template auto-escaping for product content.
- [x] Add a named URL for `/products/<int:pk>/`.
- [x] Keep both the home and detail views behind the existing `/login/` authentication redirect.

## Tests

- [x] Add model tests for product creation, decimal price persistence, non-negative price validation, and deterministic ordering as appropriate.
- [x] Add authenticated catalog tests for the greeting, product names, two-decimal prices, and product rows.
- [x] Add a test that product links point to the correct named detail URL.
- [x] Add an empty-catalog test for the clear empty state.
- [x] Add authenticated detail tests for the selected product's name and price.
- [x] Add a 404 test for an unknown product primary key.
- [x] Add anonymous-access tests confirming `/` and `/products/<int:pk>/` redirect to login.
- [x] Keep tests isolated with test-created users and products; do not require committed fixtures or local database data.

## Verification and Documentation

- [x] Run `python manage.py makemigrations core` and inspect the generated migration.
- [x] Run `python manage.py migrate --noinput`.
- [x] Run `python manage.py loaddata products` to populate representative sample products for manual verification.
- [x] Run `python manage.py check`.
- [x] Run the full Django test suite and confirm authentication and product browsing tests pass.
- [x] Start the development server and manually verify the authenticated catalog table and product detail navigation using the loaded sample products.
- [x] Inspect the diff to confirm no virtual environment, SQLite database, credentials, unintended seed data, or unrelated settings changes are staged. The planned fixture is intentional and should be reviewed for safe sample values.
- [ ] Commit implementation changes with a Conventional Commit message such as `feat: add product browsing`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [ ] Verify the feature branch and commit history before rendezvous.
- [ ] Merge the product browsing branch into `main` without overwriting unrelated changes.
- [ ] Re-run migrations, Django checks, and the full test suite on merged `main`.
- [ ] Confirm the merged application starts and serves the authenticated catalog and detail flow.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the `Product` model, catalog and detail URLs, authentication behavior, local commands, and current feature state.
