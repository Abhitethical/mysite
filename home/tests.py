from django.test import TestCase

# Create your tests here.
from celery import shared_task

from .utils import update_advertisement_status


@shared_task
def update_ads():

    update_advertisement_status()