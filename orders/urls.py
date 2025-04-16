from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, CancelOrderView, StaffOrderListView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('staff/', StaffOrderListView.as_view(), name='staff-order-list'),
]