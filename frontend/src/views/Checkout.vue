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

// True to simulate Mercado Pago flow without real redirection
const isSimulation = true; 

const userData = ref({ name: "", email: "", address: "", phone: "" });
const paymentMethod = ref('card');
const paymentData = ref({ cardNumber: "", expiryDate: "", cvc: "" });
const errors = ref({});

onMounted(() => {
  cartStore.loadCart();
  if (userStore.isAuthenticated && userStore.getUser) {
    const { name, email, address, phone } = userStore.getUser;
    userData.value = { name: name || '', email: email || '', address: address || '', phone: phone || '' };
  }
});

const totalPrice = computed(() => cartStore.totalPrice.toFixed(2));

const validateForm = () => {
    errors.value = {};
    if (!userData.value.name.trim()) errors.value.name = "Nombre es obligatorio";
    if (!userData.value.email || !/\S+@\S+\.\S+/.test(userData.value.email)) errors.value.email = "Email válido es obligatorio";
    if (paymentMethod.value === 'card') {
        if (!paymentData.value.cardNumber.replace(/\s/g, '') || !/^\d{16}$/.test(paymentData.value.cardNumber.replace(/\s/g, ''))) errors.value.cardNumber = "Número de tarjeta inválido";
        if (!paymentData.value.expiryDate || !/^\d{2}\s*\/\s*\d{2}$/.test(paymentData.value.expiryDate)) errors.value.expiryDate = "Fecha inválida (MM/AA)";
        if (!paymentData.value.cvc || !/^\d{3,4}$/.test(paymentData.value.cvc)) errors.value.cvc = "CVC inválido";
    }
    return Object.keys(errors.value).length === 0 && cartStore.totalItems > 0;
};

const submitOrder = async () => {
  if (!validateForm()) {
    toast.warning("Por favor, corrige los errores en el formulario.");
    return;
  }
  loading.value = true;
  try {
    const orderPayload = {
      items: cartStore.items.map(item => ({ id: item.id, quantity: item.quantity })),
      payment_method: paymentMethod.value,
    };

    if (paymentMethod.value === 'card') {
      orderPayload.payment_token = `sim_token_${Date.now()}`;
    }

    const orderResponse = await axios.post("/api/orders/create/", orderPayload);
    const order = orderResponse.data;

    if (paymentMethod.value === 'mercado_pago' && !isSimulation) {
      const paymentResponse = await axios.post('/api/orders/create-payment/', { order_id: order.id });
      const { init_point } = paymentResponse.data;
      window.location.href = init_point;
    } else {
      const successMessage = paymentMethod.value === 'mercado_pago' 
        ? "¡Pedido (simulado) con Mercado Pago realizado con éxito!"
        : "¡Pedido realizado con éxito!";
      toast.success(successMessage);
      cartStore.clearCart();
      router.push("/orders");
    }
  } catch (error) {
    toast.error(error.response?.data?.detail || "Error al procesar el pedido.");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="checkout-page">
    <h1>Finalizar Compra</h1>
    <div v-if="cartStore.items.length === 0" class="empty-cart card">
      <p>Tu carrito está vacío.</p>
      <router-link to="/catalog" class="btn btn-primary">Explorar productos</router-link>
    </div>
    <div v-else class="checkout-grid">
      <div class="form-container card">
        <form @submit.prevent="submitOrder">
          <section>
            <h3>Datos de Contacto y Envío</h3>
            <div class="input-group">
              <label>Nombre completo</label>
              <input v-model="userData.name" type="text" :class="{ 'input-error': errors.name }"/>
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
            <div class="input-group">
              <label>Email</label>
              <input v-model="userData.email" type="email" :class="{ 'input-error': errors.email }"/>
              <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
            </div>
          </section>

          <section>
            <h3>Método de Pago</h3>
            <div class="payment-options">
                <label :class="{ active: paymentMethod === 'card' }"><input type="radio" v-model="paymentMethod" value="card" /> Tarjeta</label>
                <label :class="{ active: paymentMethod === 'mercado_pago' }" class="mercado-pago-label"><input type="radio" v-model="paymentMethod" value="mercado_pago" /> Mercado Pago</label>
                <label :class="{ active: paymentMethod === 'cash' }"><input type="radio" v-model="paymentMethod" value="cash" /> Efectivo</label>
            </div>
            <div v-if="paymentMethod === 'card'" class="card-details">
                <div class="input-group">
                    <label>Número de Tarjeta</label>
                    <input v-model="paymentData.cardNumber" placeholder="0000 0000 0000 0000" :class="{ 'input-error': errors.cardNumber }"/>
                    <span v-if="errors.cardNumber" class="error-text">{{ errors.cardNumber }}</span>
                </div>
                <div class="payment-row">
                    <div class="input-group">
                        <label>Vencimiento</label>
                        <input v-model="paymentData.expiryDate" placeholder="MM/AA" :class="{ 'input-error': errors.expiryDate }"/>
                        <span v-if="errors.expiryDate" class="error-text">{{ errors.expiryDate }}</span>
                    </div>
                    <div class="input-group">
                        <label>CVC</label>
                        <input v-model="paymentData.cvc" placeholder="123" :class="{ 'input-error': errors.cvc }"/>
                        <span v-if="errors.cvc" class="error-text">{{ errors.cvc }}</span>
                    </div>
                </div>
            </div>
            <div v-if="paymentMethod !== 'card'" class="payment-info">
                <p v-if="paymentMethod === 'mercado_pago'">Serás redirigido a Mercado Pago para completar tu compra de forma segura.</p>
                <p v-if="paymentMethod === 'cash'">Pagarás en efectivo al momento de la entrega.</p>
            </div>
          </section>

          <button type="submit" :disabled="loading" class="btn btn-primary submit-btn">
            {{ loading ? 'Procesando...' : (paymentMethod === 'mercado_pago' ? 'Pagar con Mercado Pago' : `Finalizar Pedido (ARS ${totalPrice})`) }}
          </button>
        </form>
      </div>

      <div class="summary-container card">
        <h3>Resumen del Pedido</h3>
        <ul class="cart-items">
          <li v-for="item in cartStore.items" :key="item.id" class="cart-item">
            <img :src="item.image || '/media/default_product.jpg'" :alt="item.name"/>
            <div class="item-info">
              <span>{{ item.name }} (x{{ item.quantity }})</span>
              <strong>ARS {{ (item.price * item.quantity).toFixed(2) }}</strong>
            </div>
          </li>
        </ul>
        <div class="summary-total">
          <strong>Total a Pagar:</strong>
          <strong>ARS {{ totalPrice }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-page { max-width: 1200px; margin: 100px auto 40px; padding: var(--spacing-5); }
.checkout-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: var(--spacing-6); align-items: flex-start; }
.card { background-color: var(--color-surface); border-radius: var(--border-radius-lg); box-shadow: var(--shadow-md); padding: var(--spacing-6); }

form section { margin-bottom: var(--spacing-6); }
form h3 { margin-top: 0; margin-bottom: var(--spacing-4); border-bottom: 1px solid var(--color-border); padding-bottom: var(--spacing-2); }
.input-group { margin-bottom: var(--spacing-4); }
.input-group label { display: block; font-weight: 500; margin-bottom: var(--spacing-2); color: var(--color-text-primary); }
.input-group input { width: 100%; padding: var(--spacing-3); border: 1px solid var(--color-border); border-radius: var(--border-radius-md); font-size: 1em; }
.input-group .input-error { border-color: #ef4444; }
.error-text { color: #ef4444; font-size: 0.9em; margin-top: var(--spacing-1); }
.payment-row { display: flex; gap: var(--spacing-4); }

.payment-options { display: flex; flex-direction: column; gap: var(--spacing-3); margin-bottom: var(--spacing-5); }
.payment-options label { font-family: 'Candara', sans-serif; display: flex; align-items: center; gap: var(--spacing-3); padding: var(--spacing-3); border: 1px solid var(--color-border); border-radius: var(--border-radius-md); cursor: pointer; transition: all 0.2s ease; }
.payment-options label.active { border-color: var(--color-primary); background-color: #f0f8ff; }
.payment-options input[type="radio"] { accent-color: var(--color-primary); }

.mercado-pago-label.active { border-color: #10A4C7; background-color: #e0f7fa; }

.card-details { margin-top: var(--spacing-4); }
.payment-info { background-color: var(--color-background); padding: var(--spacing-4); border-radius: var(--border-radius-md); margin-top: var(--spacing-4); }

.summary-container h3 { margin-top: 0; }
.cart-items { list-style: none; padding: 0; margin: 0; }
.cart-item { display: flex; align-items: center; gap: var(--spacing-3); padding: var(--spacing-3) 0; border-bottom: 1px solid var(--color-border); }
.cart-item:last-child { border-bottom: none; }
.cart-item img { width: 50px; height: 50px; object-fit: cover; border-radius: var(--border-radius-sm); }
.item-info { flex-grow: 1; display: flex; justify-content: space-between; }

.summary-total { display: flex; justify-content: space-between; font-weight: 700; font-size: 1.2em; padding-top: var(--spacing-4); margin-top: var(--spacing-4); border-top: 1px solid var(--color-border); }

.submit-btn { width: 100%; padding: var(--spacing-4); font-size: 1.2em; font-family: 'Gotham', sans-serif; }
.empty-cart { text-align: center; padding: 50px; }
</style>
