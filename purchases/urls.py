from django.urls import path
from .views import (
    InvoiceCreateView,
    InvoiceListView,
    InvoiceDetailView,
    InvoiceUpdateStatusView,
    InvoiceReturnCreateView,
    InvoiceReturnListView,
    InvoiceReturnDetailView,
)

urlpatterns = [
    # ✅ Накладные
    path("invoices/create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices/<int:pk>/status/", InvoiceUpdateStatusView.as_view(), name="invoice-update-status"),

    # ✅ Возвраты накладных
    path("invoices/returns/create/", InvoiceReturnCreateView.as_view(), name="invoice-returns-create"),
    path("invoices/returns/", InvoiceReturnListView.as_view(), name="invoice-returns-list"),
    path("invoices/returns/<int:pk>/", InvoiceReturnDetailView.as_view(), name="invoice-returns-detail"),
]
