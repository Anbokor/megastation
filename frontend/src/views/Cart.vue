<script setup>
import { useCartStore } from "@/store/cart";
import { useRouter } from "vue-router";
import { ref, watch } from "vue";
import { useToast } from "vue-toastification";
import { useUserStore } from "@/store/user";

const cartStore = useCartStore();
const router = useRouter();
const toast = useToast();
const userStore = useUserStore();
const cartItems = ref(cartStore.items);

watch(() => cartStore.items, (newItems) => {
  cartItems.value = [...newItems];
}, { deep: true });

const checkout = () => {
  if (cartStore.totalItems === 0) {
    toast.warning("El carrito está vacío.");
    return;
  }
  if (!userStore.isAuthenticated) {
    toast.warning("Por favor, inicia sesión o regístrate para finalizar la compra.");
    router.push("/login");
    return;
  }
  router.push("/checkout");
};

const getDeliveryTime = (availability) => {
  return availability === "available" ? "Entrega inmediata" : "Entrega en 5-7 días";
};

const removeItem = (id) => cartStore.removeFromCart(id);
const increaseQuantity = (id) => cartStore.increaseQuantity(id);
const decreaseQuantity = (id) => cartStore.decreaseQuantity(id);

const goToCatalog = () => {
  router.push("/catalog");
};
</script>

<template>
  <div class="cart-page">
    <h1>Carrito de Compras</h1>
    <div v-if="cartStore.totalItems === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <button @click="goToCatalog" class="btn btn-primary">Explorar productos</button>
    </div>
    <div v-else class="cart-content">
      <div class="cart-list">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <img :src="item.image || '/media/default_product.jpg'" :alt="item.name" class="item-image"/>
          <div class="item-info">
            <h2>{{ item.name }}</h2>
            <p class="item-price">ARS {{ item.price }} x {{ item.quantity }}</p>
            <p class="item-total">Total: ARS {{ (item.price * item.quantity).toFixed(2) }}</p>
          </div>
          <div class="item-actions">
            <button @click="decreaseQuantity(item.id)" class="quantity-btn">-</button>
            <span class="quantity-display">{{ item.quantity }}</span>
            <button @click="increaseQuantity(item.id)" class="quantity-btn">+</button>
            <button @click="removeItem(item.id)" class="remove-btn" title="Eliminar del carrito">🗑️</button>
          </div>
        </div>
      </div>
      <div class="summary">
        <h2>Total: ARS {{ cartStore.totalPrice.toFixed(2) }}</h2>
        <button @click="checkout" class="btn btn-primary checkout-btn">Finalizar Compra</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-page { max-width: 1000px; margin: 100px auto 40px; padding: var(--spacing-5); }
.cart-content { display: grid; grid-template-columns: 2fr 1fr; gap: var(--spacing-6); }
.cart-list { display: flex; flex-direction: column; gap: var(--spacing-4); }

.cart-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.item-image { width: 80px; height: 80px; object-fit: cover; border-radius: var(--border-radius-md); }
.item-info { flex-grow: 1; }
.item-info h2 { font-size: 1.1em; margin: 0 0 var(--spacing-1) 0; }
.item-price { color: var(--color-text-secondary); margin: 0; }
.item-total { font-weight: 600; margin-top: var(--spacing-1); }

.item-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.quantity-btn, .remove-btn {
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2em;
  transition: background-color 0.2s, color 0.2s;
}

.quantity-btn:hover { background-color: var(--color-primary); color: white; }
.remove-btn { font-size: 1em; }
.remove-btn:hover { background-color: #ef4444; color: white; }
.quantity-display { font-weight: 600; min-width: 20px; text-align: center; }

.summary {
  padding: var(--spacing-5);
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: right;
  align-self: flex-start; /* Sticks to the top */
}

.summary h2 { margin: 0 0 var(--spacing-4) 0; }
.checkout-btn { width: 100%; }

.empty-cart { text-align: center; padding: 50px; }
</style>
