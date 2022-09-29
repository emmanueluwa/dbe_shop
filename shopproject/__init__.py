from __future__ import absolute_import

#ensuring celery is loaded when django starts
from .celery import app as celery_app

__all__ = ['celery_app']
