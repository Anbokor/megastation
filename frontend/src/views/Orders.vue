<script setup>
import { ref, onMounted } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import axios from "axios";

const userStore = useUserStore();
const router = useRouter();
const toast = useToast();
const orders = ref([]);
const loading = ref(false);

onMounted(async () => {
  if (!userStore.isAuthenticated) {
    toast.warning("Por favor, inicia sesión para ver tus pedidos.", {
      toastClassName: "custom-toast-warning",
    });
    router.push("/login");
    return;
  }
  await fetchOrders();
});

const fetchOrders = async () => {
  loading.value = true;
  try {
    const response = await axios.get("/api/orders/", {
      headers: { "Authorization": `Bearer ${userStore.token}` }
    });
    const ordersData = response.data;
    for (const order of ordersData) {
      for (const item of order.items) {
        const productResponse = await axios.get(`/api/store/products/${item.product}/`, {
          headers: { "Authorization": `Bearer ${userStore.token}` }
        });
        item.product = productResponse.data; // Заменяем ID на полные данные
      }
    }
    orders.value = ordersData;
  } catch (error) {
    toast.error("Error al cargar los pedidos.", {
      toastClassName: "custom-toast-error",
    });
  } finally {
    loading.value = false;
  }
};

const getStatusText = (status) => {
  const statuses = {
    'pendiente': 'Pendiente',
    'en_proceso': 'En proceso',
    'enviado': 'Enviado',
    'cancelado': 'Cancelado'
  };
  return statuses[status] || status;
};
</script>

<template>
  <div class="orders">
    <h1>📋 Mis Pedidos</h1>
    <div v-if="loading" class="loading">
      <font-awesome-icon icon="spinner" spin /> Cargando pedidos...
    </div>
    <div v-else-if="orders.length === 0" class="empty-orders">
      <p>No tienes pedidos aún.</p>
      <router-link to="/catalog" class="btn" title="Explora nuestro catálogo de productos">
        <font-awesome-icon icon="store" /> Explorar productos
      </router-link>
    </div>
    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <h2>Pedido #{{ order.id }} - {{ getStatusText(order.status) }}</h2>
        <p class="date">Fecha: {{ new Date(order.created_at).toLocaleDateString() }}</p>
        <ul class="items">
          <li v-for="item in order.items" :key="item.id" class="item">
            <img :src="item.product.image_url" :alt="item.product.name" />
            <div class="item-info">
              <h3>{{ item.product.name }}</h3>
              <p>{{ item.quantity }} x $ {{ item.product.price }}</p>
              <p class="delivery-time">{{ item.delivery_time }}</p>
            </div>
          </li>
        </ul>
        <p class="total">Total: $ {{ order.total_price }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.orders::before {
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

.orders-list {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-card {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 15px;
  background: #f9f9f9;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.order-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.date {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.items {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.item {
  display: flex;
  gap: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.item:last-child {
  border-bottom: none;
}

img {
  width: 80px;
  border-radius: 10px;
  object-fit: cover;
}

.item-info {
  flex-grow: 1;
}

.item-info h3 {
  margin: 0 0 5px;
  font-size: 1rem;
}

.item-info p {
  margin: 0;
  color: var(--color-text);
}

.delivery-time {
  font-size: 0.9rem;
  color: #666;
}

.total {
  font-weight: bold;
  color: var(--color-primary);
  text-align: right;
  margin-top: 10px;
}

.empty-orders {
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

.loading {
  text-align: center;
  padding: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .orders {
    margin: 40px auto 10px;
    padding: 15px;
  }

  .order-card {
    padding: 15px;
  }

  img {
    width: 60px;
  }

  .item-info h3 {
    font-size: 0.9rem;
  }
}
</style>