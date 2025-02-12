from celery import shared_task
from django.db.models import F
from store.models import Product
from celery.schedules import crontab
from celery import Celery
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule

app = Celery("megastation")

app.conf.beat_schedule = {
    'check-stock-every-10-minutes': {
        'task': 'store.tasks.check_stock_levels',
        'schedule': crontab(minute='*/60'),  # 🔥 Каждые 60 минут
    },
}

@shared_task
def check_stock_levels():
    """
    Verifica si hay productos con stock bajo y envía una alerta.
    """
    low_stock_products = Product.objects.filter(stock__lt=F('category__min_stock'))
    for product in low_stock_products:
        print(f"⚠️ Stock bajo: {product.name} - {product.stock} unidades")

def setup_periodic_tasks():
    # 🔥 Проверяем, есть ли уже расписание на 60 минут
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.MINUTES,
    )

    # 🔥 Проверяем, есть ли уже задача
    task, created = PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Check Stock Levels",
        task="store.tasks.check_stock_levels",
        defaults={"args": json.dumps([])},
    )

    if created:
        print("✅ Periodic task 'Check Stock Levels' creada correctamente.")
