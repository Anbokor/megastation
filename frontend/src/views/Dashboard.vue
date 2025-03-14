<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { useUserStore } from "@/store/user";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";

Chart.register(...registerables);

const userStore = useUserStore();
const loading = ref(true);
const error = ref(null);
const analytics = ref(null);
const timeFilter = ref('month');
const customDateRange = ref([null, null]);
const charts = ref({ sales: null, inventory: null, purchases: null });
const cachedAnalytics = ref({ day: null, week: null, month: null, custom: null });

const fetchAnalytics = async () => {
  try {
    loading.value = true;
    error.value = null;

    let cacheKey = timeFilter.value;
    let url = `/api/analytics/?time_filter=${timeFilter.value}`;
    if (customDateRange.value[0] && customDateRange.value[1]) {
      cacheKey = 'custom';
      const start = customDateRange.value[0].toISOString().split('T')[0];
      const end = customDateRange.value[1].toISOString().split('T')[0];
      url = `/api/analytics/?start_date=${start}&end_date=${end}`;
    }

    if (cachedAnalytics.value[cacheKey]) {
      analytics.value = cachedAnalytics.value[cacheKey];
      return;
    }

    if (!userStore.user) await userStore.fetchUser();
    if (!['superuser', 'admin', 'store_admin'].includes(userStore.getUser?.role)) {
      throw new Error('No tienes permisos');
    }

    const token = localStorage.getItem("token");
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    analytics.value = response.data;
    cachedAnalytics.value[cacheKey] = response.data;
  } catch (err) {
    error.value = err.response?.data?.error || err.message;
  } finally {
    loading.value = false;
  }
};

const createCharts = () => {
  if (charts.value.sales) charts.value.sales.destroy();
  if (charts.value.inventory) charts.value.inventory.destroy();
  if (charts.value.purchases) charts.value.purchases.destroy();

  const salesCanvas = document.getElementById('salesChart');
  if (salesCanvas) {
    const salesCtx = salesCanvas.getContext('2d');
    charts.value.sales = new Chart(salesCtx, {
      type: 'line',
      data: {
        labels: analytics.value.order_statistics.daily_sales.map(d => new Date(d.day).toLocaleDateString()),
        datasets: [{
          label: 'Ingresos Diarios ($)',
          data: analytics.value.order_statistics.daily_sales.map(d => d.revenue),
          borderColor: '#4CAF50',
          fill: false,
        }, {
          label: 'Órdenes Diarias',
          data: analytics.value.order_statistics.daily_sales.map(d => d.orders),
          borderColor: '#2196F3',
          fill: false,
        }]
      },
      options: { scales: { y: { beginAtZero: true } } }
    });
  }

  const inventoryCanvas = document.getElementById('inventoryChart');
  if (inventoryCanvas) {
    const inventoryCtx = inventoryCanvas.getContext('2d');
    charts.value.inventory = new Chart(inventoryCtx, {
      type: 'line',
      data: {
        labels: analytics.value.product_statistics.daily_stock.map(d => new Date(d.day).toLocaleDateString()),
        datasets: [{
          label: 'Cambio Diario en Stock',
          data: analytics.value.product_statistics.daily_stock.map(d => d.change),
          borderColor: '#FF9800',
          fill: false,
        }]
      },
      options: { scales: { y: { beginAtZero: false } } }
    });
  }

  const purchasesCanvas = document.getElementById('purchasesChart');
  if (purchasesCanvas) {
    const purchasesCtx = purchasesCanvas.getContext('2d');
    charts.value.purchases = new Chart(purchasesCtx, {
      type: 'line',
      data: {
        labels: analytics.value.purchase_statistics.daily_purchases.map(d => new Date(d.day).toLocaleDateString()),
        datasets: [{
          label: 'Costo Diario ($)',
          data: analytics.value.purchase_statistics.daily_purchases.map(d => d.cost),
          borderColor: '#9C27B0',
          fill: false,
        }, {
          label: 'Compras Diarias',
          data: analytics.value.purchase_statistics.daily_purchases.map(d => d.purchases),
          borderColor: '#673AB7',
          fill: false,
        }]
      },
      options: { scales: { y: { beginAtZero: true } } }
    });
  }
};

const exportToCSV = () => {
  const csvData = [];
  const headers = ['Categoría', 'Métrica', 'Valor'];
  csvData.push(headers.join(','));

  csvData.push(['Ventas', 'Total Órdenes', analytics.value.order_statistics.total_orders].join(','));
  csvData.push(['Ventas', 'Total Ingresos ($)', analytics.value.order_statistics.total_revenue].join(','));
  analytics.value.order_statistics.daily_sales.forEach(d => {
    csvData.push(['Ventas Diarias', `"${d.day} - Ingresos"`, d.revenue].join(','));
    csvData.push(['Ventas Diarias', `"${d.day} - Órdenes"`, d.orders].join(','));
  });
  analytics.value.order_statistics.top_sold_products.forEach(p => {
    csvData.push(['Top Productos Vendidos', `"${p.product__name}"`, p.total_sold].join(','));
  });

  csvData.push(['Inventario', 'Total Productos', analytics.value.product_statistics.total_products].join(','));
  csvData.push(['Inventario', 'Stock Bajo', analytics.value.product_statistics.low_stock_count].join(','));
  csvData.push(['Inventario', 'Nivel Promedio', analytics.value.product_statistics.avg_stock_level].join(','));
  analytics.value.product_statistics.daily_stock.forEach(d => {
    csvData.push(['Cambio Diario Stock', `"${d.day}"`, d.change].join(','));
  });

  csvData.push(['Compras', 'Total Compras', analytics.value.purchase_statistics.total_purchases].join(','));
  csvData.push(['Compras', 'Costo Total ($)', analytics.value.purchase_statistics.total_purchase_cost].join(','));
  analytics.value.purchase_statistics.daily_purchases.forEach(d => {
    csvData.push(['Compras Diarias', `"${d.day} - Costo"`, d.cost].join(','));
    csvData.push(['Compras Diarias', `"${d.day} - Compras"`, d.purchases].join(','));
  });
  analytics.value.purchase_statistics.top_purchased_products.forEach(p => {
    csvData.push(['Top Productos Comprados', `"${p.items__product__name}"`, p.total_purchased].join(','));
  });

  const csvContent = csvData.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'reporte_estadisticas.csv';
  link.click();
};

onMounted(async () => {
  await fetchAnalytics();
  if (analytics.value) {
    await nextTick();
    createCharts();
  }
});

watch([timeFilter, customDateRange], async () => {
  await fetchAnalytics();
  if (analytics.value) {
    await nextTick();
    createCharts();
  }
});
</script>

<template>
  <div class="dashboard">
    <h1>Panel de Control</h1>
    <div v-if="loading">Cargando...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="analytics">
      <div class="filter-section">
        <button @click="timeFilter = 'day'; customDateRange = [null, null]" :class="{ active: timeFilter === 'day' && !customDateRange[0] }">Día</button>
        <button @click="timeFilter = 'week'; customDateRange = [null, null]" :class="{ active: timeFilter === 'week' && !customDateRange[0] }">Semana</button>
        <button @click="timeFilter = 'month'; customDateRange = [null, null]" :class="{ active: timeFilter === 'month' && !customDateRange[0] }">Mes</button>
        <flat-pickr v-model="customDateRange" :config="{ mode: 'range', dateFormat: 'Y-m-d' }" placeholder="Rango personalizado"></flat-pickr>
        <button @click="exportToCSV">Exportar a CSV</button>
      </div>
      <h2>Estadísticas</h2>
      <div class="charts-container">
        <div class="chart">
          <h3>Ventas</h3>
          <canvas id="salesChart"></canvas>
          <div class="stats">
            <p>Total Órdenes: {{ analytics.order_statistics.total_orders }}</p>
            <p>Total Ingresos: ${{ analytics.order_statistics.total_revenue.toFixed(2) }}</p>
          </div>
          <h4>Top 5 Productos Vendidos</h4>
          <table>
            <thead><tr><th>Producto</th><th>Cantidad</th></tr></thead>
            <tbody>
              <tr v-for="item in analytics.order_statistics.top_sold_products" :key="item.product__name">
                <td>{{ item.product__name }}</td><td>{{ item.total_sold }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="chart">
          <h3>Inventario</h3>
          <canvas id="inventoryChart"></canvas>
          <div class="stats">
            <p>Total Productos: {{ analytics.product_statistics.total_products }}</p>
            <p>Stock Bajo: {{ analytics.product_statistics.low_stock_count }}</p>
            <p>Nivel Promedio: {{ analytics.product_statistics.avg_stock_level.toFixed(2) }}</p>
          </div>
        </div>
        <div class="chart">
          <h3>Compras</h3>
          <canvas id="purchasesChart"></canvas>
          <div class="stats">
            <p>Total Compras: {{ analytics.purchase_statistics.total_purchases }}</p>
            <p>Costo Total: ${{ analytics.purchase_statistics.total_purchase_cost.toFixed(2) }}</p>
          </div>
          <h4>Top 5 Productos Comprados</h4>
          <table>
            <thead><tr><th>Producto</th><th>Cantidad</th></tr></thead>
            <tbody>
              <tr v-for="item in analytics.purchase_statistics.top_purchased_products" :key="item.items__product__name">
                <td>{{ item.items__product__name }}</td><td>{{ item.total_purchased }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else>Sin datos</div>
  </div>
</template>

<style scoped>
.dashboard { padding: 20px; }
.error { color: red; }
.filter-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}
.filter-section button {
  padding: 8px 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}
.filter-section button.active {
  background-color: #4CAF50;
  color: white;
}
.charts-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}
.chart {
  flex: 1;
  min-width: 300px;
  background: #fff;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.chart h3 { text-align: center; }
.chart h4 { margin-top: 10px; text-align: center; }
canvas { max-width: 100%; height: 300px; }
.stats { margin-top: 10px; text-align: center; }
table {
  width: 100%;
  margin-top: 10px;
  border-collapse: collapse;
}
th, td {
  padding: 5px;
  border: 1px solid #ddd;
}
th { background-color: #f5f5f5; }
</style>