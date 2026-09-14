# User Authentication Study

## Scope

Feature 1 establishes the first usable application flow for Digital Cafe:

- Use Django's built-in `User` model and native username/password authentication.
- Require authentication before a user can view application pages.
- Provide a login page with a form and visible error messages for invalid credentials.
- Provide a home page that greets the authenticated user by username.

This feature does not include user registration, password reset, products, carts, checkout, transactions, or admin customization. Django's built-in admin remains available separately and will continue to require staff authorization.

## Current Codebase

The project is the generated `digitalcafe` Django project with a registered `core` app. Django authentication middleware, session middleware, message middleware, the built-in auth application, and the auth context processor are already enabled by the generated settings. The root URL currently exposes only `/admin/`, and `core/views.py` has no application view. The repository also contains an existing uncommitted settings change that is outside this feature and must not be overwritten.

## Feasibility

The feature is directly supported by Django's standard authentication stack. The built-in `AuthenticationForm` already validates username/password credentials and exposes non-field errors for invalid or inactive accounts. Django's `LoginView` can render and process that form, while `login_required` can protect the home view and redirect anonymous users to the login page. The built-in `User` model provides the requested username identity without a custom user migration.

## Proposed Approach

1. Add a `core` home view protected with `login_required`; render a template that displays `request.user.username`.
2. Route `/` to the protected home view.
3. Route `/login/` to Django's built-in `LoginView` using the native `AuthenticationForm` and a project-owned login template.
4. Configure the login template to render `form.non_field_errors`, field errors, and the standard username/password fields so failed submissions explain that the credentials are invalid.
5. Configure the post-login destination to the home page and the anonymous redirect destination to `/login/`.
6. Add focused tests for anonymous redirects, successful login and greeting, failed login error rendering, and protection of the application root.

The login page itself must remain publicly reachable so anonymous users have a way to authenticate. The home page and any future application URLs should use the same authentication boundary; future feature plans should explicitly apply `login_required` to their views or use an equivalent class-based access control.

## Tradeoffs

- Django's `LoginView` and `AuthenticationForm` minimize custom security-sensitive authentication code and preserve native username/password behavior.
- A project-owned template is preferable to relying on Django's nonexistent default template because it gives the application an explicit place to show validation errors and establish future styling.
- A function-based protected home view is the smallest implementation for the requested greeting and is easy to extend when the product catalog is introduced.
- A redirect for unauthenticated users is more useful than returning a 403 because it sends them directly to the login flow and preserves the original destination through Django's `next` parameter.
- No custom user model is needed. This avoids migration and compatibility costs, but changing the identity model later would require a separate, carefully planned feature before any user data depends on it.
- Tests can use Django's built-in test client and an isolated test database, avoiding a committed local SQLite database or external authentication service.

## Risks and Mitigations

- Forgetting to protect a newly added application URL could expose future pages. Mitigation: apply the protection at each view and add access-control tests as each feature is introduced.
- Rendering only field-level errors could hide the invalid-credentials message because Django's authentication failure is typically a non-field error. Mitigation: render both field errors and `non_field_errors`.
- The `next` parameter can affect post-login navigation. Mitigation: rely on Django's built-in safe redirect handling and test the default login flow without introducing custom redirect logic.
- The generated development `SECRET_KEY` and `DEBUG` settings are not production-safe. They are outside this feature's scope, but deployment work must move secrets to environment-backed settings before production use.
- Existing uncommitted settings changes must be preserved and reviewed separately; this feature must avoid broad settings rewrites.

## Verification Strategy

- Run `python manage.py check`.
- Run the core Django test suite, including tests that verify:
  - an anonymous request to `/` redirects to `/login/?next=/`;
  - the login page returns HTTP 200 and contains username/password inputs;
  - invalid credentials return the login page with a visible authentication error;
  - valid credentials redirect to `/` and the home page greets the logged-in username;
  - a logged-in session can access `/`.
- Run migrations against the ignored local SQLite database if needed to exercise the built-in auth tables.
- Start the development server and manually confirm the login page and authenticated greeting in a browser or with the Django test client.
- Confirm no local database, virtual-environment files, credentials, or unrelated settings changes are included in the feature commit.

## Open Decisions for the Plan

- Use a minimal HTML template without introducing a frontend framework or styling dependency.
- Use `/login/` as the login URL and `/` as the authenticated home URL.
- Use the username as the greeting identity because the requested authentication mechanism is Django's native username/password flow.
- Defer logout UI and route design unless the implementation plan determines it is required for a complete testable authentication flow; logout is not explicitly requested in Feature 1.
