django-serverpush
=================

Easy to use server push solution, highly integrated with django.

Requirements
------------

* Django
* Tornadio2

Introduction
------------

For any django view, you can define an update function by just naming it the
same as view function and appending "_update".

Lets say we have a view called hello that says hello to the user:

    def hello(request):
      return HttpResponse('Hey, %s!' % request.user.username)

Now we can define hello_update that returns what types of updates should affect
this page, and how will it be serialized:

* We can use default serializer and just define what fields we need:

        def hello_update(request):
          return [{'name':'username_change', 'model':User, 'params':{'pk':request.user.pk}, 'data':{'username':'object.username'}}]

    But then we have to write a special bit of JavaScript to handle this:

        $(document).bind('serverpush_username_change', function(event, data) {
          $('body').html('Hey, ' + data.username + '!');
        });

* We can write a custom serializer:

        def hello_update(request):
            # 'data' parameter is optional, and it is directly passed to the serializer
            return [{'name':'reload', 'model':User, 'params':{'pk':request.user.pk}, 'serializer':hello_update_serializer}]

        def hello_update_serializer(request, user, data):
            return 'Hey, %s!' % user.username

    And now we can either have a special JS for every page, or we can generalize
    them a bit, and have just one or a few (name in the update function is name for
    the JavaScript event).

        $(document).bind('serverpush_reload', function(event, data) {
          $('body').html(data);
        });

    In this example I called it reload, because all it does is swapping the HTML.

* Or we can just use hello view function for serializing:

        def hello_update(request):
          return [{'name':'reload', 'model':User, 'params':{'pk':request.user.pk}, 'serializer':'hello'}]

    And change hello header a bit:

        def hello(request, user=None, data=None):

    And have one general JavaScript for the whole site / updates like that
    (of course we can mix all three types of updates):

        $(document).bind('serverpush_reload', function(event, data) {
          $('body').html(data);
        });

Why django-serverpush?
----------------------

Because it's super easy to use, and requires very little additional code to
transform a traditional django application.

Installation
------------

1. Install this package

        sudo python setup.py install

2. Update settings.py

    Add "serverpush" to INSTALLED_APPS and
    "serverpush.client.context_processor" to TEMPLATE_CONTEXT_PROCESSORS.
    Also add the following constants:

        SERVERPUSH_PORT = 8013
        SERVERPUSH_NOTIFIER_PORT = 8014
        SERVERPUSH_GLOBALS = ()

3. Add a timestamp div to your template (for history to work)

        <div id="generated_timestamp" style="display:none">
          {{ generated_timestamp }}
        </div>

4. Run it by calling ./manage.py runserverpush

Running Demo
------------

1. Create sqlite file

        ./manage.py syncdb

2. Run django development server

        ./manage.py runserver

3. Run serverpush server

        ./manage.py runserverpush

4. Navigate to localhost:8000 in multiple browsers/windows/tabs and observe the counter

Browser support
---------------

It's based on socket.io, so it should work in all major browsers.
Currently there are problems with opera (because it doesn't allow cross port
XHR, and JSONP makes it "load"), but I'm working on resolving them. Simple
solution would be to proxy XHR.
