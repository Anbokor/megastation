from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_notification_emails(order_id, sales_point_id, staff_emails):
    """Send order notification emails to staff"""
    from .models import Order, SalesPoint
    order = Order.objects.get(id=order_id)
    sales_point = SalesPoint.objects.get(id=sales_point_id)

    subject = f"Nuevo pedido #{order.id} en {sales_point.name}"
    message = f"Se ha creado un nuevo pedido #{order.id} el {order.created_at}.\n" \
              f"Cliente: {order.user.username}\n" \
              f"Total: ${order.total_price}\n" \
              f"Detalles: {', '.join([f'{item.quantity} x {item.product.name}' for item in order.items.all()])}"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        staff_emails,
        fail_silently=True,
    )