<template>
  <div class="cart-container">
    <h1>🛒 Carrito de Compras</h1>

    <div v-if="cartStore.totalItems === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn">🛍️ Explorar productos</router-link>
    </div>

    <div v-else>
      <div class="cart-list">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <img :src="item.image_url || '/static/default-product.jpg'" :alt="item.name" class="cart-item-image" />
          <div class="cart-item-info">
            <h2>{{ item.name }}</h2>
            <p>💲{{ item.price }} x {{ item.quantity }}</p>
            <p>Total: 💲{{ (item.price * item.quantity).toFixed(2) }}</p>
          </div>
          <div class="cart-actions">
            <button @click="cartStore.increaseQuantity(item.id)">➕</button>
            <button @click="cartStore.decreaseQuantity(item.id)">➖</button>
            <button @click="cartStore.removeItem(item.id)">❌</button>
          </div>
        </div>
      </div>

      <div class="cart-summary">
        <h2>Total: 💲{{ cartStore.totalPrice ? cartStore.totalPrice.toFixed(2) : "0.00" }}</h2>
        <button @click="checkout" class="checkout-btn">💳 Pagar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCartStore } from "@/store/cart";
import { useRouter } from "vue-router";

const cartStore = useCartStore();
const router = useRouter();

const checkout = () => {
  if (cartStore.totalItems === 0) {
    alert("No tienes productos en el carrito.");
    return;
  }
  router.push("/checkout");
};
</script>
