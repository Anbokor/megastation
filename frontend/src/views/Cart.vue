<script setup>
import { useCartStore } from "@/store/cart";
import { useRouter } from "vue-router";
import { ref, watch } from "vue";
import { useToast } from "vue-toastification";

const cartStore = useCartStore();
const router = useRouter();
const toast = useToast();
const cartItems = ref(cartStore.items);

watch(() => cartStore.items, (newItems) => {
  cartItems.value = [...newItems];
}, { deep: true });

const checkout = () => {
  if (cartStore.totalItems === 0) {
    toast.warning("El carrito está vacío.", {
      toastClassName: "custom-toast-warning",
    });
    return;
  }
  router.push("/checkout").catch(() => {
    toast.error("Error al ir a finalizar compra.", {
      toastClassName: "custom-toast-error",
    });
  });
};

const removeItem = (id) => cartStore.removeFromCart(id);
const increaseQuantity = (id) => cartStore.increaseQuantity(id);
const decreaseQuantity = (id) => cartStore.decreaseQuantity(id);

const goToCatalog = () => {
  router.push("/catalog").catch(() => {
    toast.error("Error al ir al catálogo.", {
      toastClassName: "custom-toast-error",
    });
  });
};
</script>

<template>
  <div class="cart">
    <h1>🛒 Carrito de Compras</h1>
    <div v-if="cartStore.totalItems === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <button @click="goToCatalog" class="catalog-btn" title="Explora nuestro catálogo de productos">
        <font-awesome-icon icon="store" /> Explorar productos
      </button>
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
            <button
              @click="increaseQuantity(item.id)"
              class="action-btn increase"
              title="Aumentar cantidad"
            >
              <font-awesome-icon icon="plus" />
            </button>
            <button
              @click="decreaseQuantity(item.id)"
              class="action-btn decrease"
              title="Reducir cantidad"
            >
              <font-awesome-icon icon="minus" />
            </button>
            <button @click="removeItem(item.id)" class="action-btn remove" title="Eliminar del carrito">
              <font-awesome-icon icon="trash" />
            </button>
          </div>
        </div>
      </div>
      <div class="summary">
        <h2>Total: $ {{ cartStore.totalPrice.toFixed(2) }}</h2>
        <button @click="checkout" class="checkout-btn" title="Proceder al pago">
          <font-awesome-icon icon="credit-card" /> Finalizar Compra
        </button>
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

.actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  background: var(--color-secondary);
  color: var(--color-neutral);
  padding: 0;
  border: none;
  border-radius: 12px;
  width: 48px;
  height: 48px;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.action-btn.increase {
  background: var(--color-accent);
}

.action-btn.decrease {
  background: var(--color-primary);
}

.action-btn.remove {
  background: #D9534F;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
  filter: brightness(110%);
}

.action-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.action-btn:hover::after {
  width: 120px;
  height: 120px;
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
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
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

.catalog-btn {
  display: inline-block;
  margin-top: 15px;
  background: var(--color-secondary);
  padding: 12px 25px;
  border: none;
  border-radius: 25px;
  color: var(--color-neutral);
  font-size: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
  cursor: pointer;
}

.catalog-btn:hover {
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
    margin-top: 15px;
    gap: 15px;
  }

  .action-btn {
    width: 50px;
    height: 50px;
  }

  .summary {
    text-align: center;
    padding: 15px;
  }
}

/* Кастомизация тостов */
:deep(.custom-toast-success) {
  background-color: var(--color-primary);
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-error) {
  background-color: #D9534F;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-warning) {
  background-color: #F0AD4E;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}
</style>