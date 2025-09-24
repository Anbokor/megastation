from django.urls import path
from .views import (
    OrderListView, 
    OrderDetailView, 
    OrderCreateView, 
    CancelOrderView, 
    StaffOrderListView,
    CreatePaymentView,
    MercadoPagoWebhookView,
    StaffOrderDetailView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('webhook/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('staff/', StaffOrderListView.as_view(), name='staff-order-list'),
    path('staff/<int:pk>/', StaffOrderDetailView.as_view(), name='staff-order-detail'),
]
