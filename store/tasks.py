from celery import shared_task
from django.db.models import F
from store.models import Product
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule

@shared_task
def check_stock_levels():
    """
    ✅ Проверяет уровень запаса товаров и отправляет уведомление при низком уровне.
    """
    low_stock_products = Product.objects.filter(stock__lt=F('category__min_stock'))
    for product in low_stock_products:
        print(f"⚠️ Stock bajo: {product.name} - {product.stock} unidades")

def setup_periodic_tasks():
    """
    ✅ Устанавливает периодическую задачу, если её нет.
    """
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.MINUTES,
    )

    task, created = PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Check Stock Levels",
        task="store.tasks.check_stock_levels",
        defaults={"args": json.dumps([])},
    )

    if created:
        print("✅ Periodic task 'Check Stock Levels' creada correctamente.")
