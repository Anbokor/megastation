from django.contrib import admin
from .models import Order, OrderItem
from store.models import Product, StockMovement

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]
    actions = ['cancel_orders', 'reactivate_orders']

    def save_model(self, request, obj, form, change):
        """
        Управляет списанием и возвратом товаров при изменении статуса заказа.
        """
        if change:  # ✅ Проверяем, что заказ уже существует (не новый)
            old_order = Order.objects.get(pk=obj.pk)  # 🔥 Получаем старый статус

            # 🔥 Если заказ отменяли, а теперь активируют → нужно списать товары
            if old_order.status == "cancelado" and obj.status != "cancelado":
                self.deduct_stock(obj)

            # 🔥 Если заказ активный, а теперь отменяют → нужно вернуть товары
            elif old_order.status != "cancelado" and obj.status == "cancelado":
                self.restore_stock(obj)

        super().save_model(request, obj, form, change)

    def deduct_stock(self, order):
        """
        Списывает товары при повторной активации заказа.
        """
        stock_movements = []
        updated_products = []

        for item in order.items.all():
            if item.product.stock < item.quantity:
                raise ValueError(f"Stock insuficiente para {item.product.name}.")

            item.product.stock -= item.quantity
            updated_products.append(item.product)

            stock_movements.append(StockMovement(
                product=item.product,
                change=-item.quantity,
                reason=f"Reactivación de pedido {order.id} (Admin)"
            ))

        if updated_products:
            Product.objects.bulk_update(updated_products, ['stock'])
            StockMovement.objects.bulk_create(stock_movements)

    def restore_stock(self, order):
        """
        Возвращает товары при отмене заказа.
        """
        stock_movements = []
        updated_products = []

        for item in order.items.all():
            item.product.stock += item.quantity
            updated_products.append(item.product)

            stock_movements.append(StockMovement(
                product=item.product,
                change=item.quantity,
                reason=f"Cancelación de pedido {order.id} (Admin)"
            ))

        if updated_products:
            Product.objects.bulk_update(updated_products, ['stock'])
            StockMovement.objects.bulk_create(stock_movements)

    @admin.action(description="Cancelar pedidos seleccionados y devolver stock")
    def cancel_orders(self, request, queryset):
        """
        Массовая отмена заказов и возврат товаров.
        """
        for order in queryset:
            if order.status != "enviado":
                order.status = "cancelado"
                self.restore_stock(order)
                order.save()
        self.message_user(request, "Pedidos cancelados y stock devuelto con éxito.")

    @admin.action(description="Reactivar pedidos seleccionados y descontar stock")
    def reactivate_orders(self, request, queryset):
        """
        Массовая реактивация заказов и списание товаров.
        """
        for order in queryset:
            if order.status == "cancelado":
                order.status = "pendiente"
                self.deduct_stock(order)
                order.save()
        self.message_user(request, "Pedidos reactivados y stock descontado con éxito.")

admin.site.register(Order, OrderAdmin)
