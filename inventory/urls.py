from django.urls import path
from .views import StockListView, SalesPointListView, StockMovementListCreateView

urlpatterns = [
    path("stock/", StockListView.as_view(), name="stock-list"),
    path("sales-points/", SalesPointListView.as_view(), name="sales-point-list"),
    path("stock-movements/", StockMovementListCreateView.as_view(), name="stock-movement-list"),
]
