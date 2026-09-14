# Django Scaffold Study

## Scope

This change is intentionally limited to project scaffolding. It must not implement the requested catalog, authentication flow, cart, checkout, transaction history, or product administration behavior yet.

## Feasibility

The requested application is a good fit for Django with SQLite. Django's built-in project structure, authentication framework, admin site, ORM, migrations, and development server provide the required foundation without introducing additional dependencies. The existing Python 3.12 virtual environment is available and can hold Django and the future application dependencies.

## Approach

- Install Django into the existing `env/` virtual environment.
- Generate a Django project named `digitalcafe` at the repository root.
- Generate a `core` application and register it in `INSTALLED_APPS`.
- Keep the generated SQLite database configuration for local development.
- Preserve Django's default URL configuration and welcome page for this scaffold-only step.
- Add repository workflow documentation and ignore rules before implementation work begins.

## Tradeoffs

- Using Django's generated defaults minimizes setup risk and keeps the first change easy to verify, but leaves production hardening for a later planned feature or deployment change.
- SQLite is simple and meets the requested local database requirement, but a future production deployment may need a server database and a separate settings strategy.
- Registering `core` now establishes the application boundary without adding premature models, views, templates, or URLs.
- Django will be installed in the local environment, while dependency pinning can be added as part of a later plan once the required package set is known.

## Verification

- Run Django's system checks.
- Start the development server and request the default root page on `localhost`.
- Confirm the response is Django's default welcome page.
- Stop the server before completing this task.

## Out of Scope

- Product models or product listing/detail pages.
- User login forms or access restrictions.
- Cart, checkout, purchases, or transaction history.
- Admin customization.
- Styling, frontend templates, payments, deployment, and production settings.
