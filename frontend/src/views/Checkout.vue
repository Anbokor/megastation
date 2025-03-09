<script setup>
import { ref, computed, onMounted } from "vue";
import { useCartStore } from "@/store/cart";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import axios from "axios";

const cartStore = useCartStore();
const userStore = useUserStore();
const router = useRouter();
const toast = useToast();
const loading = ref(false);
const userData = ref({
  name: "",
  email: "",
  address: "",
  phone: "",
  paymentMethod: "card",
});
const errors = ref({});

onMounted(() => {
  cartStore.loadCart();
  if (userStore.isAuthenticated && userStore.getUser) {
    userData.value = { ...userStore.getUser, paymentMethod: "card" };
  }
});

const totalPrice = computed(() => cartStore.totalPrice.toFixed(2));
const isValid = computed(() => {
  errors.value = {};
  if (!userData.value.name.trim()) errors.value.name = "Nombre es obligatorio";
  if (!userData.value.email || !/\S+@\S+\.\S+/.test(userData.value.email)) {
    errors.value.email = "Email válido es obligatorio";
  }
  if (!userData.value.address.trim()) errors.value.address = "Dirección es obligatoria";
  if (!userData.value.phone || !/^\+?\d{9,15}$/.test(userData.value.phone)) {
    errors.value.phone = "Teléfono válido (9-15 цифр) es obligatorio";
  }
  return Object.keys(errors.value).length === 0 && cartStore.totalItems > 0;
});

const submitOrder = async () => {
  if (!isValid.value) {
    toast.warning("Por favor, corrige los errores en el formulario.", {
      toastClassName: "custom-toast-warning",
    });
    return;
  }
  loading.value = true;
  try {
    const orderData = {
      user: userData.value,
      items: cartStore.items.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
      })),
      total_price: cartStore.totalPrice,
    };
    await axios.post("/api/orders/create/", orderData);
    toast.success("¡Pedido realizado con éxito!", {
      icon: "✅",
      toastClassName: "custom-toast-success",
    });
    cartStore.clearCart();
    router.push("/").catch(() => {
      toast.error("Error al redirigir a la página principal.", {
        toastClassName: "custom-toast-error",
      });
    });
  } catch (error) {
    toast.error("Error al procesar el pedido. Intenta de nuevo.", {
      icon: "❌",
      toastClassName: "custom-toast-error",
    });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="checkout">
    <h1>🛍 Finalizar Compra</h1>
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn" title="Explora nuestro catálogo de productos">
        <font-awesome-icon icon="store" /> Explorar productos
      </router-link>
    </div>
    <div v-else class="checkout-content">
      <h2>📦 Productos en tu pedido</h2>
      <ul class="cart-items">
        <li v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <img :src="item.image_url || '/static/default-product.jpg'" :alt="item.name" />
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <p>{{ item.quantity }} x $ {{ item.price }}</p>
          </div>
        </li>
      </ul>
      <form @submit.prevent="submitOrder" class="checkout-form">
        <div v-for="(field, index) in ['name', 'email', 'address', 'phone']" :key="index" class="input-group">
          <label :title="`Introduce tu ${field === 'phone' ? 'teléfono' : field}`">
            <font-awesome-icon :icon="[field === 'name' ? 'user' : field === 'email' ? 'envelope' : field === 'address' ? 'map-marker-alt' : 'phone']" />
            {{ field === 'name' ? 'Nombre completo:' : field === 'email' ? 'Email:' : field === 'address' ? 'Dirección de envío:' : 'Teléfono:' }}
          </label>
          <input
            v-model="userData[field]"
            :type="field === 'email' ? 'email' : 'text'"
            :placeholder="`Ej: ${field === 'name' ? 'Juan Pérez' : field === 'email' ? 'juan@ejemplo.com' : field === 'address' ? 'Calle 123' : '+123456789'}`"
            @input="errors[field] = null"
            :class="{ 'error': errors[field] }"
          />
          <transition name="fade">
            <span v-if="errors[field]" class="error-text">{{ errors[field] }}</span>
          </transition>
        </div>
        <div class="input-group">
          <label title="Selecciona tu método de pago">
            <font-awesome-icon icon="credit-card" /> Método de pago:
          </label>
          <select v-model="userData.paymentMethod">
            <option value="card">💳 Tarjeta</option>
            <option value="paypal">💰 PayPal</option>
            <option value="cash">💵 Efectivo</option>
          </select>
        </div>
        <h3>Total: $ {{ totalPrice }}</h3>
        <button
          type="submit"
          :disabled="loading || !isValid"
          class="submit-btn"
          :class="{ 'loading': loading }"
          title="Confirma tu pedido"
        >
          <font-awesome-icon v-if="loading" icon="spinner" spin />
          <font-awesome-icon v-else icon="check" />
          {{ loading ? "Procesando..." : "Confirmar Pedido" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.checkout {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.checkout:hover {
  transform: translateY(-2px);
}

.checkout::before {
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

.checkout-content {
  position: relative;
  z-index: 1;
}

.cart-items {
  list-style: none;
  padding: 0;
  margin-bottom: 30px;
}

.cart-item {
  display: flex;
  gap: 20px;
  padding: 15px 0;
  border-bottom: 1px solid #ddd;
  transition: transform 0.3s ease;
}

.cart-item:hover {
  transform: translateY(-2px);
}

img {
  width: 100px;
  border-radius: 10px;
  object-fit: cover;
}

.item-info {
  flex-grow: 1;
}

.item-info h3 {
  margin: 0 0 5px;
  font-size: 1.1rem;
}

.item-info p {
  margin: 0;
  color: var(--color-text);
}

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
}

.input-group {
  text-align: left;
}

label {
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  cursor: help;
}

input,
select {
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  background: #f9f9f9;
  width: 100%;
}

input:focus,
select:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 8px rgba(16, 164, 199, 0.3);
}

input.error {
  border-color: #D9534F;
  box-shadow: 0 0 8px rgba(217, 83, 79, 0.3);
}

input::placeholder {
  color: #999;
  opacity: 0.8;
}

.error-text {
  color: #D9534F;
  font-size: 0.9rem;
  margin-top: 5px;
}

.submit-btn {
  background: var(--color-primary);
  color: var(--color-neutral);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  width: 100%;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-accent);
  transform: translateY(-2px);
}

.submit-btn:disabled {
  background: #b0b0b0;
  cursor: not-allowed;
  box-shadow: none;
}

.submit-btn.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: ripple 1.5s infinite;
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes ripple {
  0% {
    width: 0;
    height: 0;
  }
  50% {
    width: 120px;
    height: 120px;
  }
  100% {
    width: 0;
    height: 0;
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