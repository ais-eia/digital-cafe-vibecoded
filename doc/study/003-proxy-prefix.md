# Coderange Proxy Prefix Study

## Scope

Coderange exposes this Django application under `/proxy/8000/`, while the development server itself receives application paths without that external prefix. Django currently generates links such as `/products/2/`, which sends the browser outside the forwarded application path. This change should make Django-generated URLs include `/proxy/8000/` when the app is accessed through the sandbox.

The change is limited to deployment-aware URL generation and the URL paths required for the existing authentication and product browsing flows. It does not add product, cart, checkout, transaction, or authentication behavior.

## Current Codebase

The current branch is `feat/product-browsing` and contains the product browsing implementation. URL generation uses Django template `{% url %}` tags for product links, but some templates and tests still contain hard-coded root paths such as `href="/"`. Settings currently define `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `LOGIN_URL = '/login/'`, and `LOGIN_REDIRECT_URL = '/'`, with no script-prefix configuration.

The product detail route is `/products/<int:pk>/`, and the login route is `/login/`. The application is currently served at the repository-local root during ordinary development, so a prefix configuration must be applied deliberately and tested without breaking Django's test client or the local non-proxy workflow.

## Feasibility

Django supports deployment below a URL prefix through `FORCE_SCRIPT_NAME`. When set to `/proxy/8000`, Django's request script prefix and URL reversing machinery can generate paths such as `/proxy/8000/products/2/`. This is the most direct fit when the proxy strips the external prefix before forwarding requests to the Django server.

If Coderange provides a reliable proxy-prefix header and forwards it to the application, a custom middleware could derive the script prefix per request. That approach is more flexible for multiple deployments, but it introduces a header contract, trusted-proxy concerns, and more complex testing. The repository has no evidence yet of a specific forwarded-prefix header, so relying on an unverified header would be speculative.

## Proposed Approach

1. Add a deployment setting for the script prefix, preferably sourced from an environment variable and normalized to either an empty string or `/proxy/8000`.
2. Configure Django's `FORCE_SCRIPT_NAME` from that setting for the Coderange deployment. Keep the local default configurable so developers can run at `/` when no proxy prefix is present.
3. Ensure settings that represent application URLs are compatible with the prefix. In particular, avoid hard-coded `LOGIN_URL` and `LOGIN_REDIRECT_URL` values that bypass URL reversing when the prefix is enabled; use named URL resolution or prefix-aware configuration as appropriate.
4. Replace hard-coded root links in templates with `{% url %}` tags. Existing product links already use URL reversing, but the detail page's home link currently uses `href="/"` and must become prefix-aware.
5. Update tests to assert URLs through Django's reverse behavior and add coverage with the configured script prefix. Verify product links, detail-page home links, login redirects, and successful-login redirects all include `/proxy/8000/` when the prefix is active.
6. Verify request routing through the forwarding URL, not only string output. The proxy must remove or preserve the prefix consistently; if it forwards `/proxy/8000/products/2/` unchanged to Django, URLconf routing may need a prefixed mount or middleware instead of only `FORCE_SCRIPT_NAME`.

The implementation plan should first establish the actual Coderange forwarding behavior with a minimal request check or available request metadata. It should not add support for arbitrary client-controlled prefix headers unless the proxy contract and trusted source are confirmed.

## Tradeoffs

- `FORCE_SCRIPT_NAME` is a built-in Django mechanism and is preferable to custom middleware when the deployment prefix is fixed and known.
- An environment-backed prefix avoids hard-coding a sandbox-only deployment detail into application code and preserves root-relative local development when unset. It requires documenting the environment variable and setting it in the Coderange runtime.
- A fixed `FORCE_SCRIPT_NAME = '/proxy/8000'` is simpler for this sandbox but would make ordinary `localhost:8000` links point to a non-existent `/proxy/8000/` path. It is therefore only appropriate if this repository is intentionally sandbox-only.
- Reading a forwarded prefix header per request supports multiple proxy mounts but creates security risk if arbitrary clients can supply the header. It should only be considered with an explicitly trusted proxy header and middleware-level validation.
- Django URL reversing cannot repair manually written paths beginning with `/`. Converting hard-coded template links is required even if `FORCE_SCRIPT_NAME` is configured correctly.
- Keeping the public URL prefix out of the URLconf itself is preferable when the proxy strips it. Duplicating `/proxy/8000/` in URL patterns can cause double prefixes or make direct server requests fail.

## Risks and Mitigations

- The external prefix may be stripped by Coderange before the request reaches Django, or it may be forwarded unchanged. Mitigation: inspect actual request path and script-name metadata before choosing only `FORCE_SCRIPT_NAME` versus a routing/middleware adjustment.
- `LOGIN_URL` and redirect targets may remain unprefixed if they are literal strings. Mitigation: test anonymous product access and failed/successful login redirects with the prefix enabled, and use reverse-based URLs where possible.
- Cookies and CSRF behavior may be affected by the mounted path. Mitigation: exercise the login form through the forwarded HTTPS URL, retain the existing trusted origin, and verify the CSRF token submits successfully.
- A prefix setting could leak into production or local environments unexpectedly. Mitigation: use an environment variable with a safe empty default, validate that it begins with `/`, and document the Coderange value separately.
- Existing tests assert literal root paths such as `href="/"`. Mitigation: update assertions to use `reverse()` or prefix-aware expected URLs instead of weakening URL correctness.
- Static assets are not currently used beyond plain HTML, but future static URLs must also use Django's prefix-aware helpers. Mitigation: document this deployment rule for future features.

## Verification Strategy

- Run `python manage.py check` with the prefix unset and with the Coderange prefix configured.
- Run the full Django test suite in both modes if the implementation keeps local root development supported.
- Test Django `reverse('home')`, `reverse('product-detail', args=[...])`, and `reverse('login')` with `/proxy/8000` configured.
- Verify anonymous `/proxy/8000/` redirects to `/proxy/8000/login/?next=/proxy/8000/` or the exact prefix-aware equivalent produced by the chosen configuration.
- Verify the authenticated home table links to `/proxy/8000/products/<id>/`.
- Verify the detail page's home link stays under `/proxy/8000/`.
- Submit the login form through the forwarded Coderange HTTPS URL and confirm CSRF validation succeeds.
- Start the development server with the selected configuration and manually navigate from login to home to product detail without leaving the forwarded application.
- Confirm no credentials, local database, virtual-environment files, or unrelated feature changes are included.

## Open Decisions for the Plan

- Confirm whether Coderange strips `/proxy/8000` before forwarding and whether it supplies a trusted prefix header.
- Prefer an environment variable such as `DJANGO_SCRIPT_NAME=/proxy/8000` with an empty local default unless the runtime contract requires a fixed value.
- Decide whether login redirect settings should use named URL reversing in views or prefix-aware setting values while preserving Django's built-in authentication flow.
- Convert all application-generated navigation links to `{% url %}` tags; do not encode `/proxy/8000` directly into templates or URL patterns.
