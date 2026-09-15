from django.shortcuts import redirect
from django.urls import get_script_prefix, reverse, set_script_prefix


def redirect_without_script_prefix(viewname, *args, **kwargs):
    """Redirect to a named view without Django's deployment script prefix."""
    script_prefix = get_script_prefix()
    try:
        set_script_prefix('/')
        target = reverse(viewname, args=args, kwargs=kwargs)
    finally:
        set_script_prefix(script_prefix)
    return redirect(target)
