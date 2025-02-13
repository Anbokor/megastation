from django.core.mail import send_mail
from django.conf import settings


def send_order_status_email(user_email, order_id, new_status):
    """
    Sends an email notification to the customer when order status is updated.
    """
    subject = f"Tu pedido #{order_id} ha cambiado de estado"
    message = f"Hola,\n\nTu pedido ahora está en estado: {new_status}.\n\nGracias por tu compra en Megastation."

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
