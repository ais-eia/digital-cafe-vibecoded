# Live Script Name Diagnostic Plan

## Study and Branch

- [x] Record the discrepancy between local single-prefix redirects and the user's live double-prefix `Location` header.
- [ ] Create a focused diagnostic branch from the current shopping-cart branch after preserving existing work.
- [ ] Keep this change diagnostic-only; do not alter the add-to-cart redirect or permanently change prefix settings.

## Temporary Diagnostic

- [x] Add a temporary non-mutating endpoint at a clearly unique path.
- [x] Return only `request.path`, `request.path_info`, `SCRIPT_NAME`, `DJANGO_SCRIPT_NAME`, `FORCE_SCRIPT_NAME`, `HTTP_X_FORWARDED_PREFIX`, and `HTTP_X_SCRIPT_NAME`. Django 6.1 exposes the script name through `request.META['SCRIPT_NAME']`; there is no `request.script_name` attribute.
- [x] Do not return all request headers, cookies, session data, credentials, or secret settings.
- [x] Run `python manage.py check` with the diagnostic present.

## Live Probe

- [x] Start/reload the server with the same environment configuration used by Coderange.
- [x] Request the diagnostic endpoint directly on localhost.
- [ ] Request the diagnostic endpoint through the actual Coderange `/proxy/8000/` URL. Blocked: `https://itent-45-1t-2526-p21.coderange.net` was unreachable from this shell.
- [x] Record HTTP status and the safe JSON fields from each direct request.
- [x] Confirm the local response is from the current diagnostic code using its unique route.
- [x] Since the forwarded URL is unreachable from this shell, stop short of claiming the live values are known and report the exact blocker.

## Cleanup and Decision

- [x] Remove the temporary diagnostic route, view, imports, and any temporary logging.
- [x] Run `python manage.py check` after cleanup.
- [x] Run the existing cart and authentication tests after cleanup.
- [x] Document that direct local requests had `SCRIPT_NAME=/proxy/8000` because of `FORCE_SCRIPT_NAME`, with no forwarded-prefix headers; the live cause remains unresolved because the live endpoint was unreachable from this shell.
- [ ] Do not implement a permanent prefix fix until the live metadata supports a specific cause.

## Commit and Rendezvous

- [ ] If only diagnostic cleanup is needed, commit it with a Conventional Commit message such as `chore: diagnose proxy script name`.
- [ ] If a permanent fix is justified, create a separate implementation plan/commit rather than bundling an unverified settings change.
- [ ] Keep the branch unmerged and do not push `main` unless a permanent, verified fix is explicitly implemented and approved.
