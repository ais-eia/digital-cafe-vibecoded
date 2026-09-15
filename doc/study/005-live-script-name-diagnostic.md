# Live Script Name Diagnostic Study

## Scope

Investigate why the live Coderange response contains a duplicated prefix in the add-to-cart redirect:

```text
/proxy/8000/proxy/8000/cart/
```

The immediate question is whether Django receives `SCRIPT_NAME` or an equivalent WSGI/proxy value already set to `/proxy/8000`, while project settings also set `FORCE_SCRIPT_NAME` to the same value. This is a diagnostic change only. It must not change cart behavior or permanently expose request metadata.

## Current Codebase

The add-to-cart view uses `return redirect('cart')` in `core/views.py`. It does not concatenate a prefix. Django resolves the named route through URL reversing. Project settings set `FORCE_SCRIPT_NAME` from `DJANGO_SCRIPT_NAME`, defaulting to `/proxy/8000`. Local reproduction with the same setting returned a single `/proxy/8000/cart/`, which conflicts with the user's raw live response.

The prior proxy investigation used a temporary diagnostic but could not reach the Coderange hostname from the shell. The live result reported by the user is therefore the first evidence of a second prefix source in the deployed process.

## Feasibility

A temporary authenticated or non-mutating diagnostic endpoint can safely return a small allowlist of request metadata needed for this question:

- `request.path`
- `request.path_info`
- `request.script_name`
- `SCRIPT_NAME`
- `DJANGO_SCRIPT_NAME` and `FORCE_SCRIPT_NAME` as server-side configuration values
- likely proxy prefix headers, such as `HTTP_X_FORWARDED_PREFIX` and `HTTP_X_SCRIPT_NAME`

This can distinguish whether the incoming WSGI environment already has a script name, whether Django's request object sees it, and whether a proxy header is present. The endpoint must not dump all headers, cookies, session data, secret settings, or user data.

## Diagnostic Approach

1. Add a temporary route with a clearly non-production path, such as `__script-name-diagnostic__/`, returning only the allowlisted metadata.
2. Start or reload the development server using the same environment configuration as the live Coderange process.
3. Request the endpoint directly and through the Coderange forwarding URL if the external URL is reachable from this environment.
4. Compare the local and forwarded responses, especially `SCRIPT_NAME`, `request.script_name`, path values, and forwarded-prefix headers.
5. If the live endpoint is not reachable from this shell, do not infer the live values from the local response. Report the limitation and provide the exact endpoint URL and fields for the user to inspect through the live browser/devtools path.
6. Remove the diagnostic route and endpoint immediately after probing. Do not commit diagnostic code or leave it available in the application.

## Interpretation

- If the forwarded request has `SCRIPT_NAME=/proxy/8000` and settings also force `/proxy/8000`, the duplicate likely comes from combining the WSGI script name with the project-level prefix. The permanent fix should use one source of truth, not both.
- If only a forwarded-prefix header is present, the project should decide whether to trust and consume that header instead of using a fixed `FORCE_SCRIPT_NAME`.
- If the path already contains `/proxy/8000` while `SCRIPT_NAME` is also set, the proxy may be forwarding the prefix unchanged and the application may need prefix-stripping middleware rather than another `FORCE_SCRIPT_NAME` value.
- If the diagnostic values are empty locally and the live URL remains inaccessible, the root cause remains unconfirmed and no permanent settings change should be guessed from the diagnostic alone.

## Risks and Mitigations

- A diagnostic endpoint can expose deployment metadata. Mitigation: expose only the minimum fields, avoid secrets and arbitrary headers, remove it after the probe, and do not commit it.
- The endpoint may be reachable without authentication. Mitigation: use a temporary route, restrict it to safe metadata, and remove it before any commit or rendezvous.
- The live process may not reload source changes automatically. Mitigation: confirm the response contains a unique diagnostic marker and restart/reload the process if needed.
- The local shell may not reach the forwarded hostname. Mitigation: distinguish observed local values from unobserved live values and avoid claiming the question is answered when it is not.

## Verification Strategy

- Run `python manage.py check` after adding and after removing the diagnostic.
- Probe direct localhost and the actual Coderange forwarding URL, recording HTTP status and JSON payload.
- Confirm the endpoint reports no unexpected secrets or full header dump.
- Confirm the temporary route is removed from `urls.py` and the diagnostic function/import is removed from application code.
- Run the existing cart/authentication test suite after cleanup.
- Do not commit a permanent fix until the live metadata is observed or the user confirms the values from the temporary endpoint.
