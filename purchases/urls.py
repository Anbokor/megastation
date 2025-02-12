from django.urls import path
from .views import InvoiceCreateView

urlpatterns = [
    path('invoice/create/', InvoiceCreateView.as_view(), name='invoice-create'),

]
