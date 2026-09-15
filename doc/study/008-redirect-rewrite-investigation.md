# Redirect Rewrite Investigation Study

## Scope

Investigate the discrepancy between the add-to-cart view's source log and the final response:

- View-created `Location`: `/proxy/8000/cart/`
- Client-observed `Location`: `/proxy/8000/proxy/8000/cart/`

The investigation must identify whether project middleware or custom code rewrites `response['Location']`. It must not implement a permanent proxy-prefix fix until the responsible layer is identified.

## Findings To Date

- `core.views.product_detail` has one valid-add redirect: `redirect('cart')`.
- The product-detail form action uses `{% url 'product-detail' product.pk %}` and contains no hardcoded prefix.
- The cart view does not redirect authenticated users.
- `digitalcafe/settings.py` contains `FORCE_SCRIPT_NAME`, but no middleware setting that rewrites response locations.
- The configured `MIDDLEWARE` list contains only Django's generated middleware: security, sessions, common, CSRF, authentication, messages, and clickjacking protection.
- No custom middleware files exist in the repository, and repository-wide searches show no `Location` response mutation or redirect-rewriting code outside the temporary diagnostic logger.
- The temporary source log reports a single-prefix location at the view boundary.

## Standard Middleware Assessment

Django's `CommonMiddleware` can issue a new redirect for URL normalization, such as `APPEND_SLASH`, but it does not generally rewrite an existing successful redirect's `Location` header. The other configured standard middleware does not provide an application-specific prefix rewriter. Therefore, the current repository does not contain the suspected middleware layer.

The remaining possibilities are outside the visible custom application code, such as a WSGI/server wrapper, a runtime-injected middleware/settings layer, a Coderange process wrapper, or a discrepancy in how the final response was captured. The source log proves only that the view creates the single-prefix response; it does not prove which component emits the final wire response after Django's handler returns.

## Proposed Approach

1. Complete the repository inspection by checking all middleware configuration and standard middleware source behavior.
2. Remove the temporary source logger and user-run diagnostic endpoint after the live evidence has been captured.
3. Preserve the investigation result in the plan and report that no response-rewriting middleware is present in the repository.
4. Defer any permanent fix until the live process configuration or server wrapper can be inspected. Possible next evidence includes the deployed process command, WSGI/ASGI wrapper, runtime environment, or a response captured at the server socket boundary.

## Risks and Tradeoffs

- Removing the diagnostic before identifying the external layer prevents further live inspection through the current branch, but the user has already provided the decisive source-versus-client observation.
- Adding middleware to compensate without locating the existing rewrite could create a third prefix transformation and make the bug worse.
- Removing `FORCE_SCRIPT_NAME` may fix the duplicate but would likely break the already-verified proxy-prefixed URL generation unless the runtime itself supplies the script prefix.
- Standard `CommonMiddleware` behavior should not be replaced or modified for an unproven cause.

## Verification Strategy

- Run repository searches for middleware files, `MIDDLEWARE`, `Location`, redirect response mutation, `FORCE_SCRIPT_NAME`, and script-prefix handling.
- Inspect the standard Django middleware source relevant to response redirects.
- Remove temporary diagnostics and run `python manage.py check`.
- Run the existing test suite to ensure cart and authentication behavior remains unchanged.
- Do not merge, push, or implement a permanent settings change as part of this investigation-only step.
