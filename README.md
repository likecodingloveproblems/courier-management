# miare

`Miare test project`

Daily income events of couriers are stored in database, and daily income of each courier is updated in real-time, but this is only for couriers them selves to see their income.

Operation team calculate couriers income weekly, so every saturday midnight, all couriers income in that week are calculated and stored base on their daily income.

Every midnight at one morning clock, balance of previous day base on the courier income events and calculated daily income is checked and if there is any imbalance an email is sent to the admins.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

License: MIT

## Settings

Setting are configure based on the environment variables.
for database setup, `DATABASE_URL` variable is set, default is `sqlite` database.

### Authentication
Authentication is done by session and token. token authentication hit database on every request to validate token.
Another option is JSON Web Token (jwt), as it use a server side token to validate signature, it does not use database.
For more secure authentication scenario, token can be split to an access token and a refresh token, [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) is a popular option.
for more comprehensive authentication scenario [djoser](https://djoser.readthedocs.io/) can be used.

### Celery beat

celery beat periodic tasks are set in `CELERY_BEAT_SCHEDULE` variable.

For more detail look at [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).


## Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

-   To create a **superuser account**, use this command:

        $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy miare

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
cd miare
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

### Celery beat
To run a celery beat:

``` bash
cd miare
celery -A config.celery_app beat -l info
```


### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
