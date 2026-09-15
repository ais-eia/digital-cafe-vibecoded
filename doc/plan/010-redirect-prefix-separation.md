# Redirect Prefix Separation Plan

## Branch and Scope

- [x] Confirm the current diagnostic worktree and preserve the existing shopping-cart implementation.
- [x] Create a focused implementation branch from the current shopping-cart branch.
- [x] Keep `FORCE_SCRIPT_NAME` active for regular URL reversing and HTML links.
- [x] Remove the temporary raw redirect probe as part of this permanent-fix implementation.
- [x] Do not add middleware that rewrites response `Location` headers.

## Named Redirect Helper

- [x] Add a small reusable helper in an appropriate `core` utility module for named application redirects without the Django script prefix.
- [x] Support route names plus positional and keyword URL arguments needed by current and future views.
- [x] Capture the current script prefix.
- [x] Temporarily set the script prefix to `/` only while reversing the named route.
- [x] Restore the original script prefix in a `finally` block, including when URL reversing raises an exception.
- [x] Return Django's standard redirect response using the unprefixed path.
- [x] Do not accept arbitrary user-provided redirect destinations.
- [x] Replace the add-to-cart `redirect('cart')` call with the helper.
- [x] Document the helper convention for all future application-generated redirects.

## Authentication Redirect Settings

- [x] Set `LOGIN_URL` to the unprefixed `/login/` path so Coderange adds the prefix once to anonymous redirects.
- [x] Set `LOGIN_REDIRECT_URL` to the unprefixed `/` path so successful-login redirects are prefixed by Coderange once.
- [x] Keep the login template's `{% url 'login' %}` form action so regular HTML generation remains `/proxy/8000/login/` under the Coderange configuration.
- [x] Verify `next` values remain correct and do not contain a duplicated prefix.

## Tests

- [x] Test the helper returns an unprefixed `Location` while `FORCE_SCRIPT_NAME` is `/proxy/8000`.
- [x] Test the helper restores the script prefix after reversing successfully.
- [x] Test the helper restores the script prefix if reversing fails.
- [x] Test add-to-cart source and response redirects target `/cart/` locally with the configured script prefix.
- [x] Test regular `reverse('home')`, `reverse('login')`, and `reverse('product-detail')` still include `/proxy/8000/`.
- [x] Test the login form action remains `/proxy/8000/login/` in rendered HTML.
- [x] Test anonymous `@login_required` redirects use unprefixed Django `Location` values for Coderange to prefix.
- [x] Test successful login redirects use an unprefixed home target.
- [x] Test empty-prefix local development continues to work.
- [x] Preserve all existing authentication, product browsing, cart, and proxy-prefix coverage.

## Verification and Documentation

- [x] Run `python manage.py check` with the prefix unset and configured.
- [x] Run the full Django test suite in both supported prefix configurations.
- [x] Load sample products and manually exercise login, product detail, add-to-cart, and cart navigation.
- [x] Confirm the local add-to-cart response `Location` is `/cart/`, not `/proxy/8000/cart/`.
- [x] Re-run the live add-to-cart flow through Coderange and confirm the final response `Location` is exactly `/proxy/8000/cart/`. User verified this through the UI.
- [x] Confirm regular HTML links and form actions remain under `/proxy/8000/`.
- [x] Inspect the diff for temporary probe code, credentials, databases, virtual environments, and unrelated changes.
- [x] Commit with a Conventional Commit message such as `fix: separate redirect and link prefixes`.
- [x] Update this checklist as each item is completed.

## Rendezvous and Wiki Sync

- [x] Verify the implementation branch, tests, and commit history.
- [x] Merge the redirect-prefix fix into `main` without overwriting unrelated changes.
- [x] Re-run checks, tests, and live-prefix smoke verification on merged `main`.
- [x] Confirm the merged application starts and redirects correctly through Coderange.
- [ ] Push the merged `main` branch to `origin`.
- [ ] Update `doc/wiki/` with the redirect-prefix contract, helper convention, authentication redirect behavior, and verification commands.
