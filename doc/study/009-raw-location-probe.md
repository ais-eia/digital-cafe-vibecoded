# Raw Location Probe Study

## Scope

Test whether Coderange rewrites a redirect `Location` header independently of Django URL reversing and `FORCE_SCRIPT_NAME`. The temporary probe will return HTTP 302 with exactly this raw header:

```text
Location: /cart/
```

The probe must bypass `redirect()`, `reverse()`, and application prefix configuration. It must not change cart behavior or implement a permanent proxy-prefix fix.

## Current Findings

- The add-to-cart view creates `Location: /proxy/8000/cart/` at its return boundary.
- The browser/server response observed live contains `/proxy/8000/proxy/8000/cart/`.
- The product form action does not manually concatenate the prefix.
- No custom middleware or repository code rewrites response `Location` headers.
- Direct and live script-name diagnostics matched, so the remaining question is whether the proxy rewrites redirect headers after Django returns.

## Proposed Approach

1. Add a temporary unauthenticated view at `/debug-raw-redirect/`.
2. Return `HttpResponse(status=302, headers={'Location': '/cart/'})` directly.
3. Add a temporary URL pattern without `/proxy/8000` in the URLconf.
4. Run the local server and inspect the raw response headers with redirects disabled.
5. Ask the user to request `/proxy/8000/debug-raw-redirect/` through Coderange and inspect the raw `Location` header before following it.
6. Interpret the result:
   - `/cart/` proves no prefix rewrite at that layer;
   - `/proxy/8000/cart/` proves Coderange adds the external prefix to raw redirects;
   - `/proxy/8000/proxy/8000/cart/` indicates another prefix transformation or a proxy path-handling interaction.
7. Remove the temporary route and view after the result is reported. Defer any permanent settings change until the result is analyzed.

## Security and Cleanup

- The endpoint performs no database access and exposes no request metadata or secrets.
- It is intentionally unauthenticated so it can be tested through the forwarded URL.
- The response must be captured with redirect following disabled.
- Remove the endpoint immediately after the probe and run the full checks/tests.
- Do not commit or merge a permanent fix as part of this probe.
