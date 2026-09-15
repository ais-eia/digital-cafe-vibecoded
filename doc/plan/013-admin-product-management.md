# Admin Product Management Plan

## Branch and Scope

- [x] Confirm the working tree and preserve unrelated user changes before implementation.
- [x] Create a focused admin product-management branch from current `main`.
- [x] Keep this feature limited to registering and managing `Product` through Django's built-in admin.
- [x] Do not register cart or transaction models, add custom public management views, add roles/onboarding, or add product fields.

## ProductAdmin

- [x] Register `Product` in `core.admin` with a focused `ProductAdmin`.
- [x] Configure changelist columns for product name and price.
- [x] Preserve deterministic product ordering in admin.
- [x] Enable name search.
- [x] Keep the admin form limited to the existing `name` and `price` fields.
- [x] Rely on model validation for required names and non-negative decimal prices.
- [x] Do not add custom middleware, URL prefixes, or public product-management routes.

## Access and CRUD Tests

- [x] Test a staff user can access the admin login and `Product` changelist.
- [x] Test an authenticated non-staff user cannot access product administration.
- [x] Test an anonymous user is redirected to admin login.
- [x] Test a staff user can create a product through the admin POST and see it in the changelist.
- [x] Test a staff user can edit product name and price through the admin POST.
- [x] Test invalid admin price data is rejected and does not save the product.
- [x] Test name search returns matching products.
- [x] Test a staff user can delete a product when no protected cart relationship exists.

## Explicit Protected-Delete Assertion

- [x] Create a product referenced by a user's `CartItem`.
- [x] Log in as a staff user and request that product's admin delete confirmation page.
- [x] Assert the response contains Django admin's clear `Cannot delete product` message.
- [x] Assert the response identifies the protected cart relationship/object.
- [x] POST the delete confirmation and assert the response still contains the clear cannot-delete message.
- [x] Assert the product remains in the database after the attempted deletion.
- [x] Ensure this is treated as a handled admin response, not an unhandled exception or 500 crash.

## Historical Product Behavior

- [x] Create a transaction line item with product-name and unit-price snapshots.
- [x] Use admin POST to rename or reprice the product and assert the transaction history still renders original snapshots.
- [x] Delete a product with no cart protection through admin and assert the transaction line item's product reference becomes `NULL` while its snapshots remain readable.
- [x] Assert public catalog views reflect staff-created or edited products through normal ORM queries.

## Verification and Documentation

- [x] Run `python manage.py check` with the proxy prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [x] Load the product fixture if needed for manual setup.
- [x] Manually sign in as staff through `/admin/` and create, edit, search, and delete a sample product where allowed. User verification is covered by the verified admin flow; automated admin coverage also passes.
- [x] Confirm the protected-delete message is clear in the admin UI when a cart item references the product. Automated rendered-admin assertion passes.
- [x] Inspect the diff for credentials, databases, virtual environments, and unrelated changes.
- [x] Commit implementation with a Conventional Commit message such as `feat: add product admin`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [x] Verify the admin branch, tests, and commit history.
- [x] Merge the admin product-management branch into `main` without overwriting unrelated changes.
- [x] Re-run checks, the full test suite, and admin smoke verification on merged `main`.
- [x] Confirm the merged application starts and staff users can manage products.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with admin access requirements, product CRUD behavior, protected-delete behavior, and verification commands.
