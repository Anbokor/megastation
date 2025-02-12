from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, CategoryDetailView
from .views import LowStockProductsView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('low-stock/', LowStockProductsView.as_view(), name='low-stock'),
]
