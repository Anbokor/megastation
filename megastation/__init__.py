from .celery import app as celery_app  # ✅ Подключаем Celery

__all__ = ("celery_app",)
