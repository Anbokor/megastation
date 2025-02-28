<script setup>
import { useCartStore } from "@/store/cart";
import { useRouter } from "vue-router";
import { ref, watch } from "vue";

const cartStore = useCartStore();
const router = useRouter();
const cartItems = ref(cartStore.items); // Добавляем реактивность для UI

// Синхронизируем cartItems с cartStore.items
watch(() => cartStore.items, (newItems) => {
  cartItems.value = [...newItems];
}, { deep: true });

const checkout = () => {
  if (cartStore.totalItems === 0) {
    alert("El carrito está vacío.");
    return;
  }
  router.push("/checkout");
};

// Явно вызываем удаление и обновляем UI
const removeItem = (id) => {
  cartStore.removeFromCart(id);
  cartItems.value = cartStore.items; // Обновляем локальное состояние
};
</script>

<template>
  <div class="cart">
    <h1>🛒 Carrito de Compras</h1>
    <div v-if="cartStore.totalItems === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn"><font-awesome-icon icon="store" /> 🛍️ Explorar productos</router-link>
    </div>
    <div v-else class="cart-content">
      <div class="cart-list">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <img :src="item.image_url || '/static/default-product.jpg'" :alt="item.name" />
          <div class="info">
            <h2>{{ item.name }}</h2>
            <p>$ {{ item.price }} x {{ item.quantity }}</p>
            <p class="total-item">Total: $ {{ (item.price * item.quantity).toFixed(2) }}</p>
          </div>
          <div class="actions">
            <button @click="cartStore.increaseQuantity(item.id)"><font-awesome-icon icon="plus" /> ➕</button>
            <button @click="cartStore.decreaseQuantity(item.id)"><font-awesome-icon icon="minus" /> ➖</button>
            <button @click="removeItem(item.id)"><font-awesome-icon icon="trash" /> ❌</button>
          </div>
        </div>
      </div>
      <div class="summary">
        <h2>Total: $ {{ cartStore.totalPrice.toFixed(2) }}</h2>
        <button @click="checkout" class="checkout-btn"><font-awesome-icon icon="credit-card" /> 💳 Finalizar Compra</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.cart::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(23, 190, 219, 0.1), transparent);
  opacity: 0.3;
  z-index: 0;
}

.cart-content {
  position: relative;
  z-index: 1;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 15px;
  background: #f9f9f9;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.cart-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

img {
  width: 120px;
  border-radius: 10px;
  object-fit: cover;
}

.info {
  flex: 1;
  padding: 0 20px;
}

.total-item {
  font-weight: bold;
  color: var(--color-primary);
}

.actions button {
  background: var(--color-secondary);
  color: var(--color-neutral);
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

.actions button:hover {
  background: var(--color-accent-hover);
  transform: scale(1.1);
}

.summary {
  text-align: right;
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.checkout-btn {
  background: var(--color-primary);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  color: var(--color-neutral);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

.checkout-btn:hover {
  background: var(--color-accent);
  transform: translateY(-2px);
}

.empty-cart {
  text-align: center;
  padding: 30px;
}

.btn {
  display: inline-block;
  margin-top: 15px;
  background: var(--color-secondary);
  padding: 12px 25px;
  border-radius: 25px;
  color: var(--color-neutral);
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

.btn:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .cart {
    margin: 40px auto 10px;
    padding: 15px;
  }

  .cart-item {
    flex-direction: column;
    text-align: center;
  }

  img {
    width: 100px;
    margin-bottom: 10px;
  }

  .info {
    padding: 0;
  }

  .actions {
    margin-top: 10px;
  }

  .summary {
    text-align: center;
    padding: 15px;
  }
}
</style>