from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import CartItem
from .serializers import CartItemSerializer
from inventory.models import Stock

class CartListView(generics.ListCreateAPIView):
    """
    API para obtener la lista de artículos en el carrito y agregar nuevos productos.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Agrega un producto al carrito o actualiza la cantidad si ya está en el carrito.
        También verifica si hay suficiente stock disponible.
        """
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        # 🔥 Проверяем остатки на складе
        stock = Stock.objects.filter(product=product).first()
        if not stock or stock.quantity < quantity:
            raise ValidationError({"stock": "No hay suficiente stock disponible."})  # Сообщение на испанском

        # 🔥 Проверяем, есть ли товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            user=self.request.user, product=product
        )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        if cart_item.quantity < 1:
            raise ValidationError({"quantity": "La cantidad debe ser al menos 1."})  # Сообщение на испанском

        cart_item.save()

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API para obtener, actualizar la cantidad y eliminar artículos del carrito.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Actualiza la cantidad de un producto en el carrito o lo elimina si la cantidad es 0.
        También verifica si hay suficiente stock disponible.
        """
        cart_item = self.get_object()
        quantity = self.request.data.get('quantity', None)

        if quantity is None:
            raise ValidationError({"quantity": "Se requiere la cantidad."})  # Сообщение на испанском

        # 🔥 Проверяем остатки на складе перед обновлением
        stock = Stock.objects.filter(product=cart_item.product).first()
        if not stock or stock.quantity < quantity:
            raise ValidationError({"stock": "No hay suficiente stock disponible."})

        if quantity < 1:
            cart_item.delete()
        else:
            serializer.save()
