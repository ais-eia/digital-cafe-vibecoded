# User-Run Script Name Diagnostic Plan

## Study and Scope

- [x] Record that the shell cannot reach the live Coderange hostname while the user can access it through a browser.
- [x] Preserve the current shopping-cart implementation and create a focused diagnostic branch if code changes must be retained.
- [x] Keep this work diagnostic-only; do not change `FORCE_SCRIPT_NAME`, cart redirects, or proxy handling.

## Temporary Endpoint

- [x] Add a temporary non-mutating `debug_scriptname` view.
- [x] Return plain text containing `SCRIPT_NAME`, `PATH`, and `PATH_INFO`.
- [x] Include only request metadata keys beginning with `HTTP_X_FORWARDED_` or `HTTP_X_SCRIPT_NAME`.
- [x] Exclude cookies, authorization data, secrets, arbitrary environment values, and the full `request.META` mapping.
- [x] Add a temporary URL pattern at `/debug-scriptname/`, without a hardcoded `/proxy/8000` prefix.
- [x] Run `python manage.py check` with the endpoint present.

## User Probe

- [x] Request the direct local endpoint and record its plain-text output.
- [ ] Ask the user to visit `/proxy/8000/debug-scriptname/` through Coderange.
- [ ] Ask the user to paste the complete response, including all filtered header lines.
- [ ] Compare direct and live values for `SCRIPT_NAME`, `PATH`, `PATH_INFO`, and forwarded-prefix headers.
- [ ] Determine whether the duplicate prefix is caused by WSGI `SCRIPT_NAME`, a forwarded header, an already-prefixed path, or another live-only condition.

## Cleanup

- [x] Remove the temporary view, URL pattern, imports, and diagnostic-only code after the user supplies the output.
- [ ] Run `python manage.py check` after cleanup.
- [ ] Run the full existing authentication, product, proxy, and cart test suite after cleanup.
- [ ] Do not implement or commit a permanent prefix fix until the live metadata is analyzed.

## Commit and Rendezvous

- [ ] If the diagnostic must be committed for the user's deployment to load it, use a Conventional Commit such as `chore: add temporary script name diagnostic`, then remove it in a follow-up commit after the probe.
- [ ] Keep the branch unmerged while the live cause is unresolved.
- [ ] Do not push `main` as part of this diagnostic-only step.
