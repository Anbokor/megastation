from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, CancelOrderView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),  # 🔥 /api/orders/
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  # 🔥 /api/orders/1/
    path('create/', OrderCreateView.as_view(), name='order-create'),  # 🔥 /api/orders/create/
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
]