from django.core.management.base import BaseCommand
from django.utils import timezone

from home.models import Advertisement


class Command(BaseCommand):

    help = "Automatically Expire Advertisements"

    def handle(self,*args,**kwargs):

        today = timezone.localdate()

        ads = Advertisement.objects.filter(

            end_date__lte=today,

            status__in=[
                "APPROVED",
                "RUNNING"
            ]

        )

        count = 0

        for ad in ads:

            ad.status="EXPIRED"

            ad.audit_log.append({

                "action":"Automatically Expired",

                "time":str(timezone.now())

            })

            ad.save()

            count+=1

            self.stdout.write(

                self.style.WARNING(

                    f"{ad.title} Expired"

                )

            )

        self.stdout.write(

            self.style.SUCCESS(

                f"{count} Advertisements Expired"

            )

        )