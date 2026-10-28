from django.core.management.base import BaseCommand
from django.utils import timezone

from home.models import Advertisementx


class Command(BaseCommand):

    help = "Automatically update advertisement statuses"


    def handle(self, *args, **options):

        now = timezone.now()


        # APPROVED -> RUNNING

        approved_ads = Advertisementx.objects.filter(
            status="APPROVED",
            start_datetime__lte=now,
            end_datetime__gt=now
        )

        approved_count = approved_ads.update(
            status="RUNNING"
        )


        # RUNNING -> EXPIRED

        running_ads = Advertisementx.objects.filter(
            status="RUNNING",
            end_datetime__lte=now
        )

        expired_count = running_ads.update(
            status="EXPIRED"
        )


        # APPROVED -> EXPIRED
        #
        # This handles the case where the scheduler
        # missed the entire running period.

        missed_ads = Advertisementx.objects.filter(
            status="APPROVED",
            end_datetime__lte=now
        )

        missed_count = missed_ads.update(
            status="EXPIRED"
        )


        self.stdout.write(
            self.style.SUCCESS(
                f"RUNNING: {approved_count} | "
                f"EXPIRED: {expired_count + missed_count}"
            )
        )