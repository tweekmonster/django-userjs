Description
-----------

`userjs` is a Django application that produces javascript that represents a User
object.  This is useful for Django sites that are behind a cache server,
allowing you to cache the page's HTML while using javascript to modify the
page visually to show a "logout" link or something equally exciting.

The script defines a global `user` javascript object.  By default, it will
produce an object that has 1 to 3 boolean properties:

* `authenticated`
* `staff`
* `superuser`

The javascript object can be customized to include any other value you need to
represent your user objects or site's state.

This app is compatible with Django 1.4+.


Installation
------------

Add `userjs` to INSTALLED_APPS:

    INSTALLED_APPS = (
        ...
        'userjs',
        ...
    )

Add it to your project's `urls.py` file:

    urlpatterns = patterns('',
        url(r'^user\.js$', 'userjs.views.userjs', name='userjs'),
    )

Then add it to a tempalte:

    <script src="{% url 'userjs' %}"></script>



Settings
--------

### USERJS_REQUIRE_CSRF

Default: `False`

If set to `True`, loading the userjs script will set a CSRF cookie on each
request.  Even with this option disabled, adding `?csrf=1` to the script's URL
will allow you to set the cookie on demand.


### USERJS_IGNORE_EMPTY_VALUES

Default: `False`

If set to `True`, the produced script will omit properties whose values
evaluate to `False`.  This can help keep the script's size low, but you would
need to be sure that your scripts test for missing values to avoid script
errors.


### USERJS_FIELDS

The "quick" way to fill the script with simple user information.

This is a `dict` that specifies what properties should be in the produced
javascript, and what their values should be.  The values set here can either
be strings that resolve to a `User`'s field, or a callable function.  Callable
functions are passed a request object, which can be used to get the user
object.

The field values are resolved the same way query keywords are resolved.

For example:

    USERJS_FIELDS = {
        'first_name': 'first_name',
        'email': 'email__lower',
        'photo': 'photo__url',
        'server_time': labmda r: int(time.time() * 1000),
        'userid': lambda r: r.user.pk,
    }

If you need a value to actually be a static string, prefix it with `str:`

    USERJS_FIELDS = {
        ...
        'version': 'str:1.0',
        ...
    }


### USERJS_POST_PROCESSORS

This is a list of processor functions to add to the javascript output.  This
would be handy if you need something more complex than lambdas or you need to
add data that isn't available directly from the `User` object.

Each callable will be passed a `request` object and each is required to return
a `dict` or `None`.

    USERJS_POST_PROCESSORS = (
        'example_app.userjs.online_friends',
    )


### USERJS_JSON_HANDLERS

This is a list of handler functions to handle JSON parsing.  Handlers must
return a JSON-serializable value or raise `TypeError` if it doesn't handle the
object that's passed to it.

The built-in handler returns `isoformat()` for `date` and `datetime` objects.
If an object can't be handled at all, `TypeError` is raised from the default
handler.

    USERJS_JSON_HANDLERS = (
        'example_app.json_handlers.product',
    )

The product handler would look like:

    def product(obj):
        if isinstance(obj, Product):
            return {
                'name': obj.name,
                'id': obj.pk,
                'sku': obj.sku,
            }
        raise TypeError



Practical use
-------------

### A quick note

I wrote this to work with a Varnish Cache server that my company uses.  It
allowed us to keep pages cached for a _long_ time, while still allowing our
users to have an experience that's tailored for them individually.  With speed
in mind, having a frontend cache that loads a slow script would defeat the
purpose of the cache.  If you are going to make use of this app, be sure to
keep your additions lean and fast.

It should go without saying that you shouldn't include any sensitive
information in the produced script.


### Keep the script out of the cache

If you do have a cache server in front of your site, you will need to make
sure that it doesn't cache the URL you've set for the script, or URLs that
deal with changing the user's login state.  For Varnish Cache, some exceptions
would look something like the following:

    sub vcl_recv {
        # Don't cache requests to these URLs
        if (req.url ~ "^/user\.js" || req.url ~ "^/account/log(in|out)$") {
            return(pass);
        }

        # If this is a POST request, make sure it's only for /contact.
        if (req.request == "POST")
        {
            if (req.url == "/contact")
            {
                return(pass);
            }

            error 405 "Method not allowed";
        }

        # Remove cookies for other requests.
        unset req.http.Cookie;
    }


### How to use CSRF in forms on cached pages

CSRF tokens are stored in a cookie or session object.  If the CSRF or session
cookies are cached, forms will most likely fail to POST.  To deal with this,
you can use javascript to add the tokens to your forms instead of using the
`{% csrf_token %}` template tag.

    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <!-- pretend that jquery.js is loaded here -->
            <!-- also pretend that jquery.cookie.js is loaded here too -->
            <script src="{% url 'userjs' %}?csrf=1"></script>
            <script type="text/javascript">
                $(document).ready(function()
                {
                    var csrftoken = $.cookie('csrftoken');
                    if (!csrftoken)
                    {
                        console.warn('No CSRF token is available!');
                        return;
                    }

                    $('form[method="post"]').each(function(i, e)
                    {
                        $(e).append('<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '">');
                    });
                });
            </script>
        </head>
        <body>
            <form action="/contact" method="post">
                {{ contact_form.as_p }}
                <button>Submit</button>
            </form>
        </body>
    </html>


### Adding data to the script that is relevant to the the current page

There are different ways to approach this, but this example is similar to how
I do it for product pages and should give you an idea of what your options
are:

In your product template add a query string to the userjs URL (remeber this
fragment will ideally be cached for a long time):

    <script src="{% url 'userjs' %}?product={{ product.pk }}"></script>

Then create a userjs post processor:

    # Defined in example_app.userjs
    def is_favorite_product(request):
        product_pk = request.GET.get('product', 0)
        if product_pk:
            favorite_count = Favorites.objects.filter(
                user=request.user, product__pk=product_pk).count()
            return {
                'is_favorite': favorite_count > 0,
            }

Finally, add the processor to `USERJS_POST_PROCESSORS`

    USERJS_POST_PROCESSORS = (
        'example_app.userjs.is_favorite_product',
    )


### What about jsonp?

Got you covered.

    <script src="{% url 'userjs' %}?jsonp=init_user"></script>
