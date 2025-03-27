<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/store/user";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";

Chart.register(...registerables);

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);
const error = ref(null);
const analyticsData = ref(null);
const isLoaded = ref(false); // Флаг полной загрузки
const timeFilter = ref('month');
const customDateRange = ref([null, null]);
const charts = ref({ sales: null, inventory: null, purchases: null });

const fetchAnalytics = async () => {
  loading.value = true;
  error.value = null;
  isLoaded.value = false;

  try {
    let url = `/api/analytics/?time_filter=${timeFilter.value}`;
    if (Array.isArray(customDateRange.value) && customDateRange.value[0] && customDateRange.value[1]) {
      const start = customDateRange.value[0].toISOString().split('T')[0];
      const end = customDateRange.value[1].toISOString().split('T')[0];
      url = `/api/analytics/?start_date=${start}&end_date=${end}`;
    }

    if (!userStore.user) {
      try {
        await userStore.fetchUser();
      } catch (err) {
        router.push('/login');
        throw new Error("Sesión expirada, por favor inicia sesión nuevamente");
      }
    }

    if (!['superuser', 'admin', 'store_admin'].includes(userStore.getUser?.role)) {
      throw new Error('No tienes permisos');
    }

    const token = localStorage.getItem("token");
    if (!token) {
      router.push('/login');
      throw new Error("No token found");
    }

    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = response.data;
    if (!data.order_statistics || !data.product_statistics || !data.purchase_statistics) {
      throw new Error("Datos de analítica incompletos");
    }

    analyticsData.value = data;
    isLoaded.value = true; // Данные загружены
  } catch (err) {
    error.value = err.message || "Error al cargar analíticas";
    analyticsData.value = null;
    isLoaded.value = false;
    console.error("Fetch analytics error:", err);
  } finally {
    loading.value = false;
  }
};

const destroyCharts = () => {
  if (charts.value.sales) {
    charts.value.sales.destroy();
    charts.value.sales = null;
  }
  if (charts.value.inventory) {
    charts.value.inventory.destroy();
    charts.value.inventory = null;
  }
  if (charts.value.purchases) {
    charts.value.purchases.destroy();
    charts.value.purchases = null;
  }
};

const createCharts = () => {
  destroyCharts();

  if (!isLoaded.value || !analyticsData.value) return;

  const salesCanvas = document.getElementById('salesChart');
  if (salesCanvas && analyticsData.value.order_statistics.daily_sales?.length > 0) {
    const salesCtx = salesCanvas.getContext('2d');
    if (salesCtx) {
      charts.value.sales = new Chart(salesCtx, {
        type: 'line',
        data: {
          labels: analyticsData.value.order_statistics.daily_sales.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Ingresos Diarios ($)',
            data: analyticsData.value.order_statistics.daily_sales.map(d => d.revenue || 0),
            borderColor: '#4CAF50',
            fill: false,
          }, {
            label: 'Órdenes Diarias',
            data: analyticsData.value.order_statistics.daily_sales.map(d => d.orders || 0),
            borderColor: '#2196F3',
            fill: false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Ingresos', 'órdenes') } } }
        }
      });
    }
  }

  const inventoryCanvas = document.getElementById('inventoryChart');
  if (inventoryCanvas && analyticsData.value.product_statistics.daily_stock?.length > 0) {
    const inventoryCtx = inventoryCanvas.getContext('2d');
    if (inventoryCtx) {
      charts.value.inventory = new Chart(inventoryCtx, {
        type: 'line',
        data: {
          labels: analyticsData.value.product_statistics.daily_stock.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Cambio Diario en Stock',
            data: analyticsData.value.product_statistics.daily_stock.map(d => d.change || 0),
            borderColor: '#FF9800',
            fill: false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: false } },
          plugins: { tooltip: { callbacks: { label: formatTooltip(null, 'unidades') } } }
        }
      });
    }
  }

  const purchasesCanvas = document.getElementById('purchasesChart');
  if (purchasesCanvas && analyticsData.value.purchase_statistics.daily_purchases?.length > 0) {
    const purchasesCtx = purchasesCanvas.getContext('2d');
    if (purchasesCtx) {
      charts.value.purchases = new Chart(purchasesCtx, {
        type: 'line',
        data: {
          labels: analyticsData.value.purchase_statistics.daily_purchases.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Costo Diario ($)',
            data: analyticsData.value.purchase_statistics.daily_purchases.map(d => d.cost || 0),
            borderColor: '#9C27B0',
            fill: false,
          }, {
            label: 'Compras Diarias',
            data: analyticsData.value.purchase_statistics.daily_purchases.map(d => d.purchases || 0),
            borderColor: '#673AB7',
            fill: false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Costo', 'compras') } } }
        }
      });
    }
  }
};

const formatTooltip = (currencyLabel, unitLabel) => {
  return function (context) {
    let label = context.dataset.label || '';
    if (label) label += ': ';
    if (currencyLabel && context.dataset.label.includes(currencyLabel)) {
      label += new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(context.parsed.y);
    } else {
      label += context.parsed.y + ` ${unitLabel}`;
    }
    return label;
  };
};

const exportToCSV = () => {
  if (!isLoaded.value || !analyticsData.value) return;
  const csvData = [];
  const headers = ['Categoría', 'Métrica', 'Valor'];
  csvData.push(headers.join(','));

  csvData.push(['Ventas', 'Total Órdenes', analyticsData.value.order_statistics.total_orders].join(','));
  csvData.push(['Ventas', 'Total Ingresos ($)', analyticsData.value.order_statistics.total_revenue].join(','));
  analyticsData.value.order_statistics.daily_sales.forEach(d => {
    csvData.push(['Ventas Diarias', `"${d.day} - Ingresos"`, d.revenue].join(','));
    csvData.push(['Ventas Diarias', `"${d.day} - Órdenes"`, d.orders].join(','));
  });
  analyticsData.value.order_statistics.top_sold_products.forEach(p => {
    csvData.push(['Top Productos Vendidos', `"${p.product__name}"`, p.total_sold].join(','));
  });

  csvData.push(['Inventario', 'Total Productos', analyticsData.value.product_statistics.total_products].join(','));
  csvData.push(['Inventario', 'Stock Bajo', analyticsData.value.product_statistics.low_stock_count].join(','));
  csvData.push(['Inventario', 'Nivel Promedio', analyticsData.value.product_statistics.avg_stock_level].join(','));
  analyticsData.value.product_statistics.daily_stock.forEach(d => {
    csvData.push(['Cambio Diario Stock', `"${d.day}"`, d.change].join(','));
  });

  csvData.push(['Compras', 'Total Compras', analyticsData.value.purchase_statistics.total_purchases].join(','));
  csvData.push(['Compras', 'Costo Total ($)', analyticsData.value.purchase_statistics.total_purchase_cost].join(','));
  analyticsData.value.purchase_statistics.daily_purchases.forEach(d => {
    csvData.push(['Compras Diarias', `"${d.day} - Costo"`, d.cost].join(','));
    csvData.push(['Compras Diarias', `"${d.day} - Compras"`, d.purchases].join(','));
  });
  analyticsData.value.purchase_statistics.top_purchased_products.forEach(p => {
    csvData.push(['Top Productos Comprados', `"${p.items__product__name}"`, p.total_purchased].join(','));
  });

  const csvContent = csvData.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'reporte_estadisticas.csv';
  link.click();
};

const updateDashboard = async () => {
  await fetchAnalytics();
  if (isLoaded.value) createCharts();
};

onMounted(updateDashboard);

watch([timeFilter, customDateRange], updateDashboard);
</script>

<template>
  <div class="dashboard">
    <h1>Panel de Control</h1>
    <div v-if="loading">Cargando...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="isLoaded">
      <div class="filter-section">
        <button @click="timeFilter = 'day'; customDateRange = [null, null]"
                :class="{ active: timeFilter === 'day' && !customDateRange[0] }">Día
        </button>
        <button @click="timeFilter = 'week'; customDateRange = [null, null]"
                :class="{ active: timeFilter === 'week' && !customDateRange[0] }">Semana
        </button>
        <button @click="timeFilter = 'month'; customDateRange = [null, null]"
                :class="{ active: timeFilter === 'month' && !customDateRange[0] }">Mes
        </button>
        <flat-pickr v-model="customDateRange" :config="{ mode: 'range', dateFormat: 'Y-m-d' }"
                    placeholder="Rango personalizado"></flat-pickr>
        <button @click="exportToCSV">Exportar a CSV</button>
      </div>
      <h2>Estadísticas</h2>
      <div class="charts-container">
        <div class="chart">
          <h3>Ventas</h3>
          <canvas id="salesChart"></canvas>
          <div class="stats">
            <p>Total Órdenes: {{ analyticsData.order_statistics.total_orders }}</p>
            <p>Total Ingresos: ${{ analyticsData.order_statistics.total_revenue.toFixed(2) }}</p>
          </div>
          <h4>Top 5 Productos Vendidos</h4>
          <table>
            <thead>
            <tr>
              <th>Producto</th>
              <th>Cantidad</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="item in analyticsData.order_statistics.top_sold_products" :key="item.product__name">
              <td>{{ item.product__name }}</td>
              <td>{{ item.total_sold }}</td>
            </tr>
            </tbody>
          </table>
        </div>
        <div class="chart">
          <h3>Inventario</h3>
          <canvas id="inventoryChart"></canvas>
          <div class="stats">
            <p>Total Productos: {{ analyticsData.product_statistics.total_products }}</p>
            <p>Stock Bajo: {{ analyticsData.product_statistics.low_stock_count }}</p>
            <p>Nivel Promedio: {{ analyticsData.product_statistics.avg_stock_level.toFixed(2) }}</p>
          </div>
        </div>
        <div class="chart">
          <h3>Compras</h3>
          <canvas id="purchasesChart"></canvas>
          <div class="stats">
            <p>Total Compras: {{ analyticsData.purchase_statistics.total_purchases }}</p>
            <p>Costo Total: ${{ analyticsData.purchase_statistics.total_purchase_cost.toFixed(2) }}</p>
          </div>
          <h4>Top 5 Productos Comprados</h4>
          <table>
            <thead>
            <tr>
              <th>Producto</th>
              <th>Cantidad</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="item in analyticsData.purchase_statistics.top_purchased_products" :key="item.items__product__name">
              <td>{{ item.items__product__name }}</td>
              <td>{{ item.total_purchased }}</td>
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
.dashboard {
  padding: 20px;
}

.error {
  color: red;
}

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

.chart h3 {
  text-align: center;
}

.chart h4 {
  margin-top: 10px;
  text-align: center;
}

canvas {
  max-width: 100%;
  height: 300px;
}

.stats {
  margin-top: 10px;
  text-align: center;
}

table {
  width: 100%;
  margin-top: 10px;
  border-collapse: collapse;
}

th, td {
  padding: 5px;
  border: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
}
</style>