# Django Zendesk

django_zendesk provides single-sign on functionality between a
django.contrib.auth based site and Zendesk. Other authentication
systems are compatible as long as they implement the
`@login_required` decorator.   This differs from the other
implementations in that it exposes out company, external_id, tags, etc.

## SETUP

django_zendesk needs two settings.py variables to be implemented:

 * `ZENDESK_URL` : The URL of your support page, will either be on
   zendesk.com or your own domain (via a CNAME record)
 * `ZENDESK_TOKEN` : The authentication token token you receive from
   Zendesk when setting up remote authentication

The only other code setup required is pointing a URL at the
`django_zendesk.views.authorize` method, it will look something like:
```
(r'zendesk/$', 'django_zendesk.views.authorize')
```

Zendesk itself needs a bit of setup, including the URL we just set up
above and a log-out URL which already should be implemented somewhere
in your site.

Zendesk's documentation for remote authentication is [here][remote_auth] :

If you're running the tests, make sure to set the `TEST_DATABASE_CHARSET`
setting so that test databases are created to be utf8 compatible.

## CREDIT:

Initial idea by [Jon Gales](mailto:me@jongales.com) with improvements
by [Alexander Ljungberg](mailto:aljungberg@wireload.net).

See initial idea/blog post [here][intial_idea] and [here][idea2]

### Build Process:
1.  Update the `__version_info__` inside of the application. Commit and push.
2.  Tag the release with the version. `git tag <version> -m "Release"; git push --tags`
3.  Build the release `rm -rf dist build *egg-info; python setup.py sdist bdist_wheel`
4.  Upload the data `twine upload dist/*`


[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/rh0dium)

[remote_auth]: http://www.zendesk.com/api/remote_authentication
[initial_idea]: http://www.jongales.com/blog/2009/05/12/zendesk-remote-authentication-with-django/
[idea2]: https://bitbucket.org/jonknee/django_zendesk
