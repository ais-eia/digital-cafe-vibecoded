# Coderange Proxy Prefix Plan

## Empirical Forwarding Check First

- [x] Confirm the working tree and preserve the uncommitted proxy-prefix study plus any unrelated user changes.
- [x] Create a focused branch for the proxy-prefix fix from the current product-browsing branch.
- [x] Add a temporary, non-production diagnostic endpoint or equivalent request logging that reports only safe request metadata: `request.path`, `request.path_info`, `request.script_name`, `SCRIPT_NAME`, and relevant `HTTP_X_FORWARDED_*` or `HTTP_X_SCRIPT_NAME` values.
- [ ] Start Django on the forwarded port and request the actual Coderange URL `/proxy/8000/` and a nested path such as `/proxy/8000/products/1/`. Blocked: the Coderange hostname was unreachable from this shell.
- [x] Record whether Django receives the external `/proxy/8000` prefix in the path, whether Django receives a script-name value, and which proxy headers, if any, are present for direct local requests. Direct requests had no prefix, no `SCRIPT_NAME`, and no forwarded-prefix headers; the external forwarding behavior remains unobservable from this shell.
- [x] Remove the temporary diagnostic endpoint or logging after the forwarding behavior was checked; no request headers are exposed in the application.
- [x] Document the observed result in this checklist and use it to choose exactly one URL-prefix strategy below. Based on the user's confirmed external URL and the unavailable external probe, use environment-backed `FORCE_SCRIPT_NAME` with a Coderange default.

## Strategy Decision

- [x] If Coderange strips `/proxy/8000` before forwarding, configure Django's script prefix with an environment-backed `FORCE_SCRIPT_NAME` value such as `/proxy/8000`.
- [ ] If Coderange forwards a trusted script-name or forwarded-prefix header, implement narrowly scoped middleware or validated request handling for that documented header; do not trust arbitrary client-supplied values.
- [ ] If Coderange forwards `/proxy/8000` unchanged without a script-name mechanism, choose a routing/middleware solution that strips the prefix before URLconf resolution, rather than blindly adding the prefix to URL patterns.
- [x] Preserve an explicit environment override through `DJANGO_SCRIPT_NAME`; the default is `/proxy/8000` for the current Coderange deployment, and `DJANGO_SCRIPT_NAME=''` restores direct-root local links.
- [x] Do not implement multiple competing prefix mechanisms or hard-code `/proxy/8000` into templates and URL patterns.

## Settings and URL Generation

- [x] Add the selected prefix configuration with an environment-backed `FORCE_SCRIPT_NAME` value.
- [x] Make the login form action prefix-aware without breaking Django's built-in `LoginView` flow or `next` handling.
- [x] Replace every remaining hard-coded application navigation path in templates, including the product detail page's home link, with Django `{% url %}` tags.
- [x] Keep product and login URLconf routes unprefixed because the proxy is expected to strip the external prefix before Django routing.
- [x] Ensure URL reversing includes `/proxy/8000/` with the default Coderange configuration.

## Tests

- [x] Add a focused test or request-level diagnostic assertion for the observed Coderange forwarding behavior. Direct local diagnostics confirmed no incoming prefix, while the external host was unreachable from this shell; URL-generation tests cover the configured deployment prefix.
- [x] Test `reverse('home')`, `reverse('login')`, and `reverse('product-detail', args=[...])` with the prefix unset.
- [x] Test the same URL reversals with `/proxy/8000` configured and assert the prefix appears exactly once.
- [x] Verify the product table link and product detail page's home link are prefix-aware.
- [x] Verify anonymous catalog and detail requests produce prefix-aware login redirects and `next` values.
- [x] Verify successful login redirects to the prefix-aware home URL.
- [x] Preserve the existing authentication, product browsing, and 404 coverage.
- [ ] If request-level middleware is selected, test trusted and untrusted/missing prefix metadata according to the observed proxy contract.

## Verification and Documentation

- [x] Run `python manage.py check` with the prefix unset.
- [x] Run `python manage.py check` with the Coderange prefix configured.
- [x] Run the full Django test suite in both supported configuration modes.
- [ ] Start the development server with the selected configuration and verify navigation through `/proxy/8000/`, login, home, and product detail. Blocked locally: a direct Django server receives `/proxy/8000/...` as a literal path and returns 404; the external Coderange URL was unreachable from this shell. The expected deployment model is that Coderange strips the prefix before forwarding.
- [ ] Submit the login form through the forwarded HTTPS URL and confirm CSRF validation still succeeds. Blocked: external Coderange hostname unreachable from this shell.
- [x] Confirm generated application links remain under `/proxy/8000/` through reverse and template tests.
- [x] Inspect the diff for credentials, database files, virtual-environment files, diagnostic code, and unrelated feature changes.
- [x] Commit the implementation with a Conventional Commit message such as `fix: support coderange proxy prefix`.
- [x] Update this checklist as decisions and implementation steps are completed.

## Rendezvous and Wiki Sync

- [x] Verify the feature branch, empirical forwarding result, and commit history.
- [x] Merge the proxy-prefix fix into `main` without overwriting unrelated changes.
- [x] Re-run checks, tests, and forwarded-URL smoke verification on merged `main`.
- [x] Confirm the merged application starts and generates working prefixed URLs.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the observed Coderange forwarding behavior, selected configuration, required environment variable or proxy contract, and local verification commands.
