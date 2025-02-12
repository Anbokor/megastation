from django.contrib import admin
from .models import CartItem

@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity")
    search_fields = ("user__username", "product__name")
    list_filter = ("user",)
