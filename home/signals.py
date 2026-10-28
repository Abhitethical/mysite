from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Customer, CustomerLoginLogout,timezone

@receiver(user_logged_in)
def log_customer_login(sender, request, user, **kwargs):
    customer = Customer.objects.get(user=user)
    CustomerLoginLogout.objects.create(customer=customer)

@receiver(user_logged_out)
def log_customer_logout(sender, request, user, **kwargs):
    customer = Customer.objects.get(user=user)
    last_record = CustomerLoginLogout.objects.filter(customer=customer, logout_time__isnull=True).last()
    if last_record:
        last_record.logout_time = timezone.now()
        last_record.save()












from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserLoginHistory

@receiver(user_logged_in)
def track_login(sender, user, request, **kwargs):
    # Create a new login record for this user
    UserLoginHistory.objects.create(user=user, login_time=timezone.now())

@receiver(user_logged_out)
def track_logout(sender, user, request, **kwargs):
    # Update the latest login record with logout time
    last_login = UserLoginHistory.objects.filter(user=user, logout_time__isnull=True).last()
    if last_login:
        last_login.logout_time = timezone.now()
        last_login.save()






from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserLoginHistory
from django.utils import timezone

@receiver(user_logged_in)
def create_login_history(sender, request, user, **kwargs):
    UserLoginHistory.objects.create(user=user)

@receiver(user_logged_out)
def update_logout_history(sender, request, user, **kwargs):
    try:
        # Find the latest login record without logout_time
        history = UserLoginHistory.objects.filter(user=user, logout_time__isnull=True).latest('login_time')
        history.logout_time = timezone.now()
        history.save()
    except UserLoginHistory.DoesNotExist:
        pass
















from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfilexx

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfilexx.objects.create(
            user=instance,
            role='SELLER'   # default role
        )
