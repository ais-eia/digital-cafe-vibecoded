# Add-to-Cart Redirect Source Plan

## Study and Scope

- [x] Confirm the valid authenticated add flow has one expected Django redirect: `product_detail` to `cart`.
- [x] Confirm the product detail form action uses Django URL reversing and has no manually concatenated proxy prefix.
- [x] Keep this work diagnostic-only; do not change prefix settings or cart redirect behavior.

## Temporary Source Logging

- [x] Add a module logger to `core.views`.
- [x] Construct the existing `redirect('cart')` response in a local variable.
- [x] Log only the generated `Location`, request path, `SCRIPT_NAME`, and route context.
- [x] Return the unchanged redirect response.
- [x] Do not log cookies, credentials, sessions, request bodies, or all request metadata.
- [x] Keep the existing `/debug-scriptname/` endpoint available while the user performs the live probe.

## Local Verification

- [x] Run `python manage.py check`.
- [x] Run the full existing test suite.
- [x] Render the product detail page and verify the form action contains one configured prefix.
- [x] Perform a local valid add-to-cart POST and verify the source log and response `Location` contain one prefix.
- [x] Confirm the authenticated flow has one redirect hop and the cart GET returns `200`.

## Live Probe

- [x] Ask the user to confirm `/proxy/8000/debug-scriptname/` still returns the diagnostic output.
- [x] Ask the user to trigger one valid add-to-cart POST through the live UI.
- [x] Ask the user to capture the temporary server log line containing the generated source `Location`.
- [x] Compare the source log `Location` with the raw browser response `Location`.
- [x] Record that duplication occurs after the view creates its response.

## Cleanup and Follow-up

- [x] Remove the temporary logger and `/debug-scriptname/` endpoint after the live output is analyzed.
- [ ] Run `python manage.py check` and the full test suite after cleanup.
- [x] Do not implement a permanent prefix fix until the source-level result identifies the cause.
- [x] If a permanent fix is needed, create a separate study and plan rather than mixing it into this diagnostic.
- [x] Keep the branch unmerged and do not push `main` for this diagnostic step.
