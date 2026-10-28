from .models import Advertisement


def update_advertisement_status():

    ads = Advertisement.objects.all()

    for ad in ads:
        ad.refresh_status()