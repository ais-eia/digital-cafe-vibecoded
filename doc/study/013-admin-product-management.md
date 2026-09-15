# Admin Product Management Study

## Scope

Feature 6 exposes product management through Django's built-in admin panel. An administrator should be able to create, view, edit, and delete `Product` records directly in `/admin/`, with the existing product name and decimal price fields.

This feature does not add a custom admin theme, public product-management views, staff onboarding, custom user roles, transaction administration, cart administration, bulk import, image uploads, categories, search, or product fields beyond the current model.

## Current Codebase

The Django admin application and `/admin/` URL are already enabled. `core.admin` currently contains only the generated placeholder and does not register any model. `Product` has a bounded name and non-negative two-decimal price. Its `PROTECT` relationship from `CartItem` prevents deleting a product while it is in a user's cart, while transaction line items use `SET_NULL` and retain product-name/price snapshots for historical purchases.

The built-in `User` and admin authentication are already available. Admin access is controlled by Django's `is_staff` permission, so non-staff users should not be able to manage products. The Coderange `/proxy/8000` prefix affects public URL generation but does not require a custom admin URL pattern.

## Feasibility

Registering `Product` with a `ModelAdmin` is directly supported by Django. The admin can provide list display for name and price, search by name, ordering, and a simple form for editing the two model fields. Existing model validators and database constraints enforce price validity regardless of whether data comes from the public fixture, ORM, or admin form.

No migration is required because the model already contains the needed fields. Admin tests can use Django's test client and a staff user, with an isolated test database. Product deletion behavior should be tested against both cart protection and transaction snapshot preservation because admin deletion invokes the same model relationships as any other deletion path.

## Proposed Approach

1. Register `Product` in `core.admin` with a focused `ProductAdmin`.
2. Configure list display for `name` and `price`, ordering by the existing model ordering, and search by `name`.
3. Keep the admin form limited to `name` and `price`, relying on model validation for required names and non-negative decimal prices.
4. Verify staff users can access the product changelist, create products, edit names/prices, and delete products when relationships permit.
5. Verify non-staff authenticated users and anonymous users cannot access product administration.
6. Verify deleting a product with a pending `CartItem` is blocked, while deleting a product referenced only by transaction line items preserves the line-item snapshot and nulls the optional product reference.
7. Keep public catalog behavior unchanged; admin edits should be reflected by the existing product list/detail pages through normal ORM queries.

## Tradeoffs

- Using Django's native admin minimizes custom management UI and inherits staff permissions, CSRF protection, validation, pagination, and form handling.
- A minimal `ModelAdmin` avoids adding fields or workflows not requested. Name search and name/price list display are useful operational defaults without expanding scope.
- Leaving transaction and cart models unregistered reduces the risk of administrators mutating historical purchases or user carts accidentally. Product deletion still follows model relationship policies.
- Admin remains at Django's standard `/admin/` route. Adding a custom prefix or public product-management route would create unnecessary security and maintenance surface.
- The admin will allow product deletion where the database permits it. Cart `PROTECT` and transaction-line `SET_NULL` policies remain the authoritative data-integrity behavior.

## Risks and Mitigations

- Registering a model alone does not guarantee non-staff access is blocked if permissions are misconfigured. Mitigation: test staff, authenticated non-staff, and anonymous clients.
- Editing a product price changes future cart and checkout display prices but must not change completed transaction history. Mitigation: test admin edits followed by history rendering.
- Deleting a product with a cart row should not silently remove a user's pending item. Mitigation: preserve `PROTECT` and test the admin delete response/error behavior.
- A product deleted through admin could be absent from public browsing while historical lines remain. Mitigation: test `SET_NULL` plus snapshots and document the behavior.
- Admin URLs may be affected by the deployment prefix if manually hardcoded in navigation. Mitigation: use Django's standard admin URL resolution and test only the route that the existing URLconf provides.
- Admin changes can create products not represented in the optional fixture. Mitigation: keep fixtures for repeatable manual setup but do not require or overwrite admin data.

## Verification Strategy

- Run `python manage.py check` with both prefix configurations.
- Run the full Django test suite.
- Test `/admin/` login and product changelist access for a staff user.
- Test non-staff and anonymous denial of product administration.
- Test staff creation and rendered changelist visibility for a product.
- Test staff editing of product name and price through admin POST, including validation rejection for invalid prices.
- Test permitted product deletion and protected deletion when a cart item exists.
- Test completed transaction snapshots remain unchanged after an admin product rename, repricing, or deletion.
- Test public product browsing still shows admin-created products after the admin operation.
- Manually sign in as a staff user through the Django admin and create/edit/delete a sample product.
