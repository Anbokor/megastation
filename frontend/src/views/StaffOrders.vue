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
    toast.warning("Por favor, inicia sesión para ver los pedidos del personal.", {
      toastClassName: "custom-toast-warning",
    });
    router.push("/login");
    return;
  }
  await fetchStaffOrders();
});

const fetchStaffOrders = async () => {
  loading.value = true;
  try {
    const response = await axios.get("/api/orders/staff/", {
      headers: { "Authorization": `Bearer ${userStore.token}` }
    });
    orders.value = response.data;
  } catch (error) {
    toast.error("Error al cargar los pedidos del personal.", {
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
  <div class="staff-orders">
    <h1>📋 Pedidos del Personal</h1>
    <div v-if="loading" class="loading">
      <font-awesome-icon icon="spinner" spin /> Cargando pedidos...
    </div>
    <div v-else-if="orders.length === 0" class="empty-orders">
      <p>No hay pedidos disponibles para tu tienda.</p>
    </div>
    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <h2>Pedido #{{ order.id }} - {{ getStatusText(order.status) }}</h2>
        <p class="date">Fecha: {{ new Date(order.created_at).toLocaleDateString() }}</p>
        <ul class="items">
          <li v-for="item in order.items" :key="item.id" class="item">
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
.staff-orders {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.staff-orders::before {
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

.loading {
  text-align: center;
  padding: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .staff-orders {
    margin: 40px auto 10px;
    padding: 15px;
  }

  .order-card {
    padding: 15px;
  }

  .item-info h3 {
    font-size: 0.9rem;
  }
}
</style>