from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import CartItem
from .serializers import CartItemSerializer

class CartListView(generics.ListCreateAPIView):
    """API to list and add items to the cart"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Add or update a product in the cart"""
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            user=self.request.user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity < 1:
                cart_item.delete()
                return
            cart_item.save()

        serializer.instance = cart_item

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API to retrieve, update, or delete cart items"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """Update quantity or delete if quantity is 0"""
        cart_item = self.get_object()
        quantity = self.request.data.get('quantity', None)

        if quantity is None:
            raise ValidationError({"quantity": "Se requiere la cantidad."})

        if quantity < 1:
            cart_item.delete()
        else:
            serializer.save()