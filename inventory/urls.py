from django.urls import path
from .views import StockListView, SalesPointListView

urlpatterns = [
    path("stock/", StockListView.as_view(), name="stock-list"),
    path("sales-points/", SalesPointListView.as_view(), name="sales-point-list"),
]
