<script setup>
import { ref, computed, onMounted } from "vue";
import { useCartStore } from "@/store/cart";
import axios from "axios";
import { useRouter } from "vue-router";

const cartStore = useCartStore();
const router = useRouter();

// Поля формы
const userData = ref({
  name: "",
  email: "",
  address: "",
  phone: "",
  paymentMethod: "card",
});

// Сохранение корзины при обновлении страницы
onMounted(() => {
  cartStore.loadCart();
});

// Валидация
const isValid = computed(() => {
  return userData.value.name && userData.value.email && userData.value.address && userData.value.phone;
});

const submitOrder = async () => {
  if (!isValid.value) {
    alert("Por favor completa todos los campos.");
    return;
  }

  try {
    const orderData = {
      user: userData.value,
      items: cartStore.items.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
      })),
      total_price: cartStore.totalPrice,
    };

    await axios.post("http://127.0.0.1:8000/api/orders/create/", orderData);
    alert("¡Pedido realizado con éxito!");
    cartStore.clearCart();
    router.push("/");
  } catch (error) {
    alert("Hubo un error al procesar el pedido.");
  }
};
</script>

<template>
  <div class="checkout-container">
    <h1>🛍 Finalizar Compra</h1>

    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn">Explorar productos</router-link>
    </div>

    <div v-else>
      <h2>📦 Productos en tu pedido</h2>
      <ul class="cart-items">
        <li v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <img :src="item.image_url" :alt="item.name" class="product-image" />
          <div>
            <h3>{{ item.name }}</h3>
            <p>{{ item.quantity }} x 💲{{ item.price }}</p>
          </div>
        </li>
      </ul>

      <h2>📄 Información del Cliente</h2>
      <form @submit.prevent="submitOrder" class="checkout-form">
        <label>Nombre completo:</label>
        <input type="text" v-model="userData.name" required />

        <label>Email:</label>
        <input type="email" v-model="userData.email" required />

        <label>Dirección de envío:</label>
        <input type="text" v-model="userData.address" required />

        <label>Teléfono:</label>
        <input type="text" v-model="userData.phone" required />

        <label>Método de pago:</label>
        <select v-model="userData.paymentMethod">
          <option value="card">💳 Tarjeta de crédito</option>
          <option value="paypal">💰 PayPal</option>
          <option value="cash">💵 Pago en efectivo</option>
        </select>

        <h3>Total: 💲{{ cartStore.totalPrice }}</h3>
        <button type="submit" :disabled="!isValid">✅ Confirmar Pedido</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.checkout-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.cart-items {
  list-style: none;
  padding: 0;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
}

.product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 5px;
}

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input, select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

button {
  background-color: #17BEDB;
  color: white;
  border: none;
  padding: 10px;
  margin-top: 10px;
  cursor: pointer;
  border-radius: 5px;
}

button:disabled {
  background-color: gray;
  cursor: not-allowed;
}
</style>
