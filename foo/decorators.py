### Decorators for request handlers ###


def post_required(func):
    """Decorator that returns an error unless request.method == 'POST'."""

    def post_wrapper(request, *args, **kwds):
        if request.method != 'POST':
            return HttpResponse('This requires a POST request.', status=405)
        return func(request, *args, **kwds)

    return post_wrapper


def login_required(func):
    """Decorator that redirects to the login page if you're not logged in."""

    def login_wrapper(request, *args, **kwds):
        if request.user is None:
            return HttpResponseRedirect(
                users.create_login_url(request.get_full_path().encode('utf-8')))
        return func(request, *args, **kwds)

    return login_wrapper


def xsrf_required(func):
    """Decorator to check XSRF token.

    This only checks if the method is POST; it lets other method go
    through unchallenged.  Apply after @login_required and (if
    applicable) @post_required.  This decorator is mutually exclusive
    with @upload_required.
    """

    def xsrf_wrapper(request, *args, **kwds):
        if request.method == 'POST':
            post_token = request.POST.get('xsrf_token')
            if not post_token:
                return HttpResponse('Missing XSRF token.', status=403)
            account = models.Account.current_user_account
            if not account:
                return HttpResponse('Must be logged in for XSRF check.', status=403)
            xsrf_token = account.get_xsrf_token()
            if post_token != xsrf_token:
                # Try the previous hour's token
                xsrf_token = account.get_xsrf_token(-1)
                if post_token != xsrf_token:
                    return HttpResponse('Invalid XSRF token.', status=403)
        return func(request, *args, **kwds)

    return xsrf_wrapper


def upload_required(func):
    """Decorator for POST requests from the upload.py script.

    Right now this is for documentation only, but eventually we should
    change this to insist on a special header that JavaScript cannot
    add, to prevent XSRF attacks on these URLs.  This decorator is
    mutually exclusive with @xsrf_required.
    """
    return func


def admin_required(func):
    """Decorator that insists that you're logged in as administratior."""

    def admin_wrapper(request, *args, **kwds):
        if request.user is None:
            return HttpResponseRedirect(
                users.create_login_url(request.get_full_path().encode('utf-8')))
        if not request.user_is_admin:
            return HttpResponseForbidden('You must be admin in for this function')
        return func(request, *args, **kwds)

    return admin_wrapper

