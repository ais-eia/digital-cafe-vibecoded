# Redirect Rewrite Investigation Plan

## Repository Inspection

- [x] Inspect `MIDDLEWARE` in `digitalcafe/settings.py`.
- [x] Search for custom middleware files.
- [x] Search for code that mutates `response['Location']` or rewrites redirect URLs.
- [x] Inspect the add-to-cart form action and redirect path for hardcoded prefix concatenation.
- [x] Inspect standard Django middleware behavior relevant to response redirects.

## Diagnostic Cleanup

- [x] Preserve the source-level finding that the view creates `/proxy/8000/cart/`.
- [ ] Remove the temporary add-to-cart redirect logger.
- [ ] Remove the temporary `/debug-scriptname/` view and URL route.
- [ ] Remove diagnostic-only imports and ensure no temporary instrumentation remains.
- [ ] Run `python manage.py check` after cleanup.
- [ ] Run the full existing test suite after cleanup.

## Findings and Follow-up

- [x] Record that no custom middleware or repository code rewrites `Location`.
- [x] Record that standard `CommonMiddleware` can issue normalization redirects but is not an existing-location prefix rewriter.
- [ ] Report the remaining likely layer as runtime/server/proxy code outside this repository.
- [ ] Do not implement a permanent prefix change until the external rewriting layer is identified.
- [ ] Keep this investigation branch unmerged and do not push `main` for this step.
