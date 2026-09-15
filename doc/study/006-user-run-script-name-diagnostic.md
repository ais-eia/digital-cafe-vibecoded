# User-Run Script Name Diagnostic Study

## Scope

The local shell cannot reach the live Coderange hostname, but the user can open the forwarded application in a browser. This diagnostic will add a temporary plain-text endpoint at `/debug-scriptname/` so the user can inspect the live request metadata through the Coderange proxy and paste the result back for analysis.

The endpoint must report only the fields needed to determine why Django emits the duplicated redirect prefix:

- `request.META['SCRIPT_NAME']`
- `request.path`
- `request.path_info`
- `HTTP_X_FORWARDED_*` headers
- `HTTP_X_SCRIPT_NAME` headers

It must not change cart behavior, alter prefix settings, expose cookies or credentials, dump all request headers, or remain in the application after the user has captured the output.

## Current Codebase

The current branch is `feat/shopping-cart`. The add-to-cart view uses the named redirect `redirect('cart')`; it contains no manual prefix concatenation. `digitalcafe/settings.py` configures `FORCE_SCRIPT_NAME` from `DJANGO_SCRIPT_NAME`, defaulting to `/proxy/8000`. Local requests with that configuration generate one prefix, while the user observed a raw live `Location` header with two prefixes.

The previous diagnostic study and checklist are present as `doc/study/005-live-script-name-diagnostic.md` and `doc/plan/005-live-script-name-diagnostic.md`. Those diagnostics were removed after local probing because the live host was unreachable from the shell. The user-run endpoint is the appropriate next step because it observes the actual forwarded request in the environment where the duplication occurs.

## Feasibility

A small Django view returning plain text is sufficient. Django exposes the WSGI script name through `request.META['SCRIPT_NAME']`; `request.path` and `request.path_info` show how the request is represented after script-prefix handling. Header inspection can be limited to keys beginning with `HTTP_X_FORWARDED_` or `HTTP_X_SCRIPT_NAME`, with values included as plain text.

The endpoint should be unauthenticated and non-mutating so it can be opened directly even when the normal application pages require login. Its path should be unique and easy for the user to visit through the proxy. A temporary route is preferable to logging because the user can inspect the exact live response and paste it back without requiring shell access to server logs.

## Diagnostic Approach

1. Add a temporary `debug_scriptname` view that builds a deterministic plain-text report.
2. Include `SCRIPT_NAME`, `PATH`, `PATH_INFO`, and all request metadata keys whose names begin with `HTTP_X_FORWARDED_` or `HTTP_X_SCRIPT_NAME`.
3. Add a temporary URL pattern at `/debug-scriptname/`. Do not include `/proxy/8000` in the URLconf pattern; the external proxy is responsible for the mount prefix.
4. Run Django's system check and, if possible, request the direct local endpoint to establish a comparison response.
5. Ask the user to visit `/proxy/8000/debug-scriptname/` through Coderange and paste the complete plain-text response.
6. Once the output is received, determine whether the duplicate is caused by an incoming script name, a forwarded-prefix header, an already-prefixed path, or another deployment setting.
7. Remove the temporary view, route, imports, and any diagnostic-only documentation/checklist changes that should not remain as application behavior. Do not implement the permanent fix until the live output has been analyzed.

## Security and Cleanup

- The endpoint must return only path/script-name metadata and explicitly filtered prefix headers.
- Do not expose `SECRET_KEY`, cookies, authorization headers, session data, arbitrary environment variables, or the full `request.META` mapping.
- Do not add authentication state, database queries, or mutation logic.
- Mark the endpoint temporary in the implementation checklist and remove it promptly after the user supplies the output.
- Run `python manage.py check` and the existing tests after cleanup.
- Do not commit or push a permanent fix based only on an unverified assumption.

## Verification Strategy

- Run `python manage.py check` with the temporary route present.
- Request the local endpoint and confirm the output contains the expected field labels and no secret values.
- Have the user request the forwarded endpoint and paste its output.
- Compare local and live values for `SCRIPT_NAME`, `PATH`, `PATH_INFO`, and filtered prefix headers.
- Remove the diagnostic code and route after analysis.
- Run `python manage.py check` and the full existing test suite after cleanup.
- Keep the branch unmerged until the live cause is identified and a separate permanent-fix plan is approved.
