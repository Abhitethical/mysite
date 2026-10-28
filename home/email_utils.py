# accounts/email_utils.py
from django.core.mail import send_mail
from django.conf import settings

# email_utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user):
    subject = 'Welcome to Our Website!'
    message = f'Hi {user.username},\n\nThank you for registering with us!'
    from_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'no-reply@example.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)



from django.core.mail import send_mail
from django.conf import settings

def send_order_email(user, placed_orders):
    subject = "Order Confirmation"
    message = f"Hi {user.get_full_name() or user.username},\n\n"
    message += "Thank you for your order! Here are the details:\n\n"

    for order in placed_orders:
        message += (
            f"Product: {order.product}\n"
            f"Quantity: {order.quantity}\n"
            f"Name: {order.name}\n"
            f"Address: {order.address}, {order.city}, {order.state}, {order.postal_code}\n"
            f"Phone: {order.phone}\n"
            f"Status: {order.status}\n\n"
        )

    message += "We will process your order soon.\n\nBest regards,\nYour Shop Team"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
