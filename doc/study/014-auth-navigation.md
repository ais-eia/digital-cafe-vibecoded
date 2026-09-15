# Login and Logout Navigation Study

## Scope

Feature 7 adds a shared navigation bar to the public application templates. Authenticated pages should show a consistent menu with navigation links and a logout control. The login page should not show the authenticated navigation bar or logout control.

This feature does not change authentication credentials, user registration, password reset, admin navigation, authorization rules, or the existing product/cart/checkout/history behavior.

## Current Codebase

The application uses Django's built-in `LoginView` at `/login/`, but there is no logout URL or UI. Each application template is currently a standalone HTML document with repeated links. Authenticated pages include home, product detail, cart, checkout, checkout confirmation, and transaction history. The login template is separate and publicly accessible.

The project uses `FORCE_SCRIPT_NAME` for `/proxy/8000` HTML URL generation and `redirect_without_script_prefix()` for application redirects because Coderange prefixes redirect `Location` headers. Django 6.1's logout flow is POST-oriented, so the navigation logout control should be a CSRF-protected form rather than a GET link.

## Feasibility

Django provides `LogoutView` and session invalidation through its built-in authentication views. A shared base template can provide one navigation bar to all authenticated pages while login remains a standalone template without that base. The existing app templates can extend the base and retain their current page-specific content.

The logout form can post to a named `/logout/` route and redirect to the login page after success. The form action should use `{% url 'logout' %}` so it includes the Coderange prefix in HTML. The logout response target should be unprefixed for Coderange to prefix once, consistent with the existing redirect contract.

## Proposed Approach

1. Add a project-owned `core/base.html` with a shared navigation bar.
2. Include links to the home/catalog, cart, checkout, and transaction history using named URL tags.
3. Include the current username and a CSRF-protected POST logout form.
4. Configure a named `/logout/` route using Django's built-in `LogoutView` with a login-page redirect target.
5. Convert authenticated application templates to extend the base template.
6. Keep `login.html` independent of the base template so the login page has no authenticated navigation or logout control.
7. Add tests across representative authenticated pages and the login page, including logout session invalidation, redirect behavior, CSRF form presence, and prefix-aware generated actions.

The navigation should be visible on every authenticated application page, including pages with empty states and purchase confirmation. Django admin remains outside the shared public template and keeps its own navigation.

## Tradeoffs

- A shared base template removes repeated navigation markup and makes future links consistent, but requires converting all current application templates to template inheritance.
- A POST logout form follows Django's current security expectations and prevents logout through crawlers or ordinary GET links. It is slightly more markup than an anchor.
- A built-in `LogoutView` avoids custom session code and preserves Django behavior.
- The login page remains standalone to ensure anonymous users do not see links intended for authenticated users.
- A base template link to every current authenticated destination improves discoverability but should remain limited to existing routes rather than anticipating future features.
- No custom CSS or frontend dependency is needed; the feature is navigation structure and behavior only.

## Risks and Mitigations

- Forgetting to extend the base on one authenticated page would create inconsistent navigation. Mitigation: convert and test every current public application template.
- A logout anchor using GET could violate the intended safe logout flow. Mitigation: use a CSRF-protected POST form and test the form action/method.
- A logout form action or redirect could be double-prefixed under Coderange. Mitigation: use `{% url 'logout' %}` for the HTML action and an unprefixed `next_page`/redirect target for the response.
- The login page could accidentally inherit authenticated navigation. Mitigation: keep it standalone and assert it lacks the navigation marker and logout control.
- Logout should invalidate the session fully. Mitigation: test that the client can no longer access a protected page after posting logout.
- Existing tests may assert page-specific markup without the new base structure. Mitigation: preserve page content and update only assertions that depend on document structure.

## Verification Strategy

- Run `python manage.py check` with both prefix configurations.
- Run the full Django test suite.
- Assert the navigation appears on home, product detail, cart, checkout, checkout confirmation, and transaction history for authenticated users.
- Assert the navigation contains named links and a POST logout form with CSRF token.
- Assert the login page returns HTTP 200 but contains no logout form or authenticated navigation marker.
- POST logout as an authenticated user and assert the response redirects to the prefix-aware login URL at the client boundary and protected pages require login afterward.
- Assert generated navigation and logout form URLs include `/proxy/8000` in HTML when configured.
- Manually verify login, navigation, logout, and post-logout protection through the Coderange UI.
