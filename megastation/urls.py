from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from analytics.views import AnalyticsView  # Добавляем импорт

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/store/', include('store.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/', include('cart.urls')),
    path('api/purchases/', include('purchases.urls')),
    path("api/inventory/", include("inventory.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/analytics/", AnalyticsView.as_view(), name="analytics"),  # Добавляем маршрут
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)