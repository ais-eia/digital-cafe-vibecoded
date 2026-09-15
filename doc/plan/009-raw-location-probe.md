# Raw Location Probe Plan

## Preparation

- [x] Confirm the add-to-cart source location is single-prefix and repository middleware does not rewrite it.
- [x] Keep the change diagnostic-only and avoid changing `FORCE_SCRIPT_NAME` or cart behavior.

## Temporary Probe

- [x] Add an unauthenticated `debug_raw_redirect` view.
- [x] Return HTTP 302 with exactly `Location: /cart/` using `HttpResponse` headers.
- [x] Add `/debug-raw-redirect/` to the URLconf without a hardcoded proxy prefix.
- [x] Run `python manage.py check`.
- [x] Request the local endpoint with redirect following disabled and record its raw `Location` header.

## Live Probe

- [x] Ask the user to visit `/proxy/8000/debug-raw-redirect/` through Coderange.
- [x] Ask the user to inspect the raw response `Location` header before the browser follows it.
- [x] Compare the live header with the local `/cart/` baseline.
- [x] Record that Coderange adds one prefix to raw redirect locations.

## Cleanup

- [x] Remove the temporary view and URL route after the user reports the header.
- [x] Run `python manage.py check` and the full test suite after cleanup.
- [x] Analyze the result in a separate permanent-fix study/plan if a settings or runtime change is required.
- [x] Keep this branch unmerged and do not push `main` for the diagnostic probe.
