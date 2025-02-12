import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "megastation.settings")

app = Celery("megastation")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Celery работает! ID задачи: {self.request.id}")
