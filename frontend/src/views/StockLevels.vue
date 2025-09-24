<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const stockItems = ref([]);
const loading = ref(true);
const toast = useToast();

// Filter states
const searchQuery = ref('');

// Fetch stock levels from the backend
onMounted(async () => {
  try {
    const response = await axios.get('/api/inventory/stock/');
    stockItems.value = response.data;
  } catch (error) {
    toast.error('Error al cargar los niveles de stock.');
    console.error('Failed to fetch stock levels:', error);
  } finally {
    loading.value = false;
  }
});

// Computed property to filter stock items
const filteredStockItems = computed(() => {
  if (!searchQuery.value) {
    return stockItems.value;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return stockItems.value.filter(item =>
    item.product_name.toLowerCase().includes(lowerCaseQuery) ||
    item.sales_point_name.toLowerCase().includes(lowerCaseQuery)
  );
});

const getStatusClass = (item) => {
  if (item.quantity <= 0) return 'status-out-of-stock';
  if (item.is_low_stock) return 'status-low-stock';
  return 'status-in-stock';
};

const getStatusText = (item) => {
  if (item.quantity <= 0) return 'Agotado';
  if (item.is_low_stock) return 'Bajo Stock';
  return 'En Stock';
};
</script>

<template>
  <div class="stock-container">
    <h1>Niveles de Stock</h1>

    <div class="filters">
      <input type="text" v-model="searchQuery" placeholder="Buscar por producto o punto de venta..." class="search-input" />
    </div>

    <div v-if="loading" class="loading-spinner">
      <font-awesome-icon icon="spinner" spin size="3x" />
      <p>Cargando stock...</p>
    </div>
    <div v-else-if="filteredStockItems.length > 0" class="stock-table-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Punto de Venta</th>
            <th>Cantidad</th>
            <th>Reservado</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredStockItems" :key="item.id">
            <td>{{ item.product_name }}</td>
            <td>{{ item.sales_point_name }}</td>
            <td>{{ item.quantity }}</td>
            <td>{{ item.reserved_quantity }}</td>
            <td>
              <span :class="['status-badge', getStatusClass(item)]">
                {{ getStatusText(item) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="no-stock">
      <p>No se encontraron artículos en el inventario.</p>
    </div>
  </div>
</template>

<style scoped>
.stock-container { max-width: 1200px; margin: 40px auto; padding: 30px; background: var(--color-neutral); border-radius: 15px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); }
.filters { margin-bottom: 20px; }
.search-input { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
.loading-spinner, .no-stock { text-align: center; padding: 40px; color: var(--color-text-muted); }
.stock-table-container { overflow-x: auto; }
.stock-table { width: 100%; border-collapse: collapse; }
.stock-table th, .stock-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
.stock-table th { background-color: #f8f9fa; font-weight: 500; }

.status-badge { padding: 5px 10px; border-radius: 15px; color: white; font-size: 0.9em; }
.status-in-stock { background-color: #28a745; }
.status-low-stock { background-color: #ffc107; color: #333; }
.status-out-of-stock { background-color: #dc3545; }
</style>
