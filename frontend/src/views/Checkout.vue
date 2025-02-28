<script setup>
import { ref, computed, onMounted } from "vue";
import { useCartStore } from "@/store/cart";
import { useUserStore } from "@/store/user";
import axios from "axios";
import { useRouter } from "vue-router";

const cartStore = useCartStore();
const userStore = useUserStore();
const router = useRouter();

const userData = ref({
  name: "",
  email: "",
  address: "",
  phone: "",
  paymentMethod: "card",
});

onMounted(() => {
  cartStore.loadCart();
  if (userStore.isAuthenticated && userStore.getUser) {
    userData.value = { ...userStore.getUser, paymentMethod: "card" };
  }
});

const totalPrice = computed(() => cartStore.totalPrice.toFixed(2));
const isValid = computed(() =>
  userData.value.name && userData.value.email && userData.value.address && userData.value.phone
);

const submitOrder = async () => {
  if (!isValid.value) {
    alert("Por favor completa todos los campos.");
    return;
  }
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
    alert("¡Pedido realizado con éxito!");
    cartStore.clearCart();
    router.push("/");
  } catch (error) {
    alert("Error al procesar el pedido.");
  }
};
</script>

<template>
  <div class="checkout">
    <h1>🛍 Finalizar Compra</h1>
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn"><font-awesome-icon icon="store" /> 🛍️ Explorar productos</router-link>
    </div>
    <div v-else class="checkout-content">
      <h2>📦 Productos en tu pedido</h2>
      <ul class="cart-items">
        <li v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <img :src="item.image_url || '/static/default-product.jpg'" :alt="item.name" />
          <div>
            <h3>{{ item.name }}</h3>
            <p>{{ item.quantity }} x $ {{ item.price }}</p>
          </div>
        </li>
      </ul>
      <form @submit.prevent="submitOrder" class="checkout-form">
        <label><font-awesome-icon icon="user" /> Nombre completo:</label>
        <input v-model="userData.name" required />
        <label><font-awesome-icon icon="envelope" /> Email:</label>
        <input type="email" v-model="userData.email" required />
        <label><font-awesome-icon icon="map-marker-alt" /> Dirección de envío:</label>
        <input v-model="userData.address" required />
        <label><font-awesome-icon icon="phone" /> Teléfono:</label>
        <input v-model="userData.phone" required />
        <label><font-awesome-icon icon="credit-card" /> Método de pago:</label>
        <select v-model="userData.paymentMethod">
          <option value="card">💳 Tarjeta</option>
          <option value="paypal">💰 PayPal</option>
          <option value="cash">💵 Efectivo</option>
        </select>
        <h3>Total: $ {{ totalPrice }}</h3>
        <button type="submit" :disabled="!isValid"><font-awesome-icon icon="check" /> ✅ Confirmar Pedido</button>
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

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
}

label {
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
}

input, select {
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease;
}

input:focus, select:focus {
  border-color: var(--color-primary);
  outline: none;
}

button {
  background: var(--color-primary);
  color: var(--color-neutral);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

button:disabled {
  background: gray;
}

button:hover:not(:disabled) {
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
  .checkout {
    margin: 40px auto 10px;
    padding: 15px;
  }

  .cart-item {
    flex-direction: column;
    text-align: center;
  }

  img {
    width: 80px;
    margin-bottom: 10px;
  }

  .checkout-form {
    gap: 15px;
  }
}
</style>