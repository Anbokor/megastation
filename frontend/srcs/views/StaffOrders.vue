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
const loading = ref(true);

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
    console.error("Error fetching staff orders:", error);
  } finally {
    loading.value = false;
  }
};

// Function to navigate to the detail page
const goToOrderDetail = (orderId) => {
  router.push(`/staff/orders/${orderId}`);
};

const getStatusClass = (status) => {
    return `status-${status}`;
};

// FIX: Add a robust date formatting function
const formatDate = (dateString) => {
    if (!dateString) return 'Fecha no disponible';
    const date = new Date(dateString);
    if (isNaN(date)) {
        return 'Fecha inválida';
    }
    return date.toLocaleDateString();
};

</script>

<template>
  <div class="staff-orders-page">
    <h1 class="page-title">📋 Pedidos del Personal</h1>
    <div v-if="loading" class="loading-state">Cargando...</div>
    <div v-else-if="orders.length === 0" class="empty-state card">
      <p>No se encontraron pedidos.</p>
    </div>
    <div v-else class="orders-table-container card">
      <table class="orders-table">
        <thead>
          <tr>
            <th>ID Pedido</th>
            <th>Cliente</th>
            <th>Fecha</th>
            <th>Total</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" @click="goToOrderDetail(order.id)" class="order-row">
            <td>#{{ order.id }}</td>
            <td>{{ order.user?.username || 'N/A' }}</td>
            <!-- FIX: Use the robust formatDate function -->
            <td>{{ formatDate(order.created_at) }}</td>
            <td>ARS {{ Number(order.total_price).toFixed(2) }}</td>
            <td>
              <span :class="['status-badge', getStatusClass(order.status)]">{{ order.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.staff-orders-page {
  max-width: 1200px;
  margin: 40px auto;
  padding: 2rem;
}

.page-title {
  margin-bottom: 2rem;
  text-align: center;
}

.card {
  background-color: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  padding: 2rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem;
  font-size: 1.2rem;
  color: var(--color-text-secondary);
}

.orders-table-container {
  overflow-x: auto;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.orders-table th, .orders-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.orders-table th {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.order-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.order-row:hover {
  background-color: var(--color-background-muted);
}

.status-badge {
  padding: 0.25em 0.6em;
  font-size: 0.9em;
  font-weight: 600;
  border-radius: 15px;
  color: white;
  text-transform: capitalize;
}

.status-pendiente { background-color: #f59e0b; }
.status-en_proceso { background-color: #3b82f6; }
.status-enviado { background-color: #8b5cf6; }
/* FIX: Add styles for new statuses */
.status-completado { background-color: #22c55e; }
.status-cancelado { background-color: #71717a; }
.status-fallido { background-color: #ef4444; }
</style>
