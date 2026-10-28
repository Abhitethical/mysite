from django.utils import timezone

from .models import Advertisement


def update_advertisement_status():

    now = timezone.now()

    # APPROVED -> RUNNING

    approved_ads = Advertisement.objects.filter(
        status="APPROVED",
        start_datetime__lte=now
    )

    for ad in approved_ads:

        ad.status = "RUNNING"
        ad.save()


    # RUNNING -> EXPIRED

    running_ads = Advertisement.objects.filter(
        status="RUNNING",
        end_datetime__lte=now
    )

    for ad in running_ads:

        ad.status = "EXPIRED"
        ad.save()