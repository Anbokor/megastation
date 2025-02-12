from django.urls import path
from .views import CartListView, CartDetailView

urlpatterns = [
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', CartDetailView.as_view(), name='cart-detail'),
]
