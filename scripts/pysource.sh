#!/bin/bash
DJANGO_SETTINGS_MODULE=settings python -c "import $1 ; print $1"  | sed -e "s/.*'\(.*\)\/__init.*/\1/" | xargs mate

#mate /Users/christopheradams/coding/genentech_project/Source_Services/env-Source_Services/lib/python2.7/site-packages/django/
