<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/store/user";
import { useToast } from "vue-toastification";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";

Chart.register(...registerables);

const userStore = useUserStore();
const router = useRouter();
const toast = useToast();
const loading = ref(false);
const error = ref(null);
const analyticsData = ref(null);
const isLoaded = ref(false);
const timeFilter = ref('month');
const customDateRange = ref([null, null]);
const charts = ref({ sales: null, inventory: null, purchases: null, salesBySalesPoint: null, salesByCustomer: null });
const chartType = ref('line');
const salesPointFilter = ref(null);
const customerFilter = ref(null);
const salesPoints = ref([]);
const customers = ref([]);

const fetchSalesPointsAndCustomers = async () => {
  if (!userStore.isAuthenticated || !userStore.token) {
    toast.warning("Por favor, inicia sesión para continuar.", {
      toastClassName: "custom-toast-warning",
    });
    router.push("/login");
    return;
  }

  try {
    // Fetch SalesPoints from inventory
    const salesPointResponse = await axios.get("/api/inventory/sales-points/", {
      headers: { Authorization: `Bearer ${userStore.token}` },
    });
    salesPoints.value = salesPointResponse.data;
  } catch (err) {
    console.error("Error fetching SalesPoints:", err);
    salesPoints.value = [];
    toast.error("Error al cargar puntos de venta.", {
      toastClassName: "custom-toast-error",
    });
  }

  try {
    // Fetch Customers
    const customerResponse = await axios.get("/api/users/customers/", {
      headers: { Authorization: `Bearer ${userStore.token}` },
    });
    customers.value = customerResponse.data;
  } catch (err) {
    console.error("Error fetching Customers:", err);
    customers.value = [];
    toast.error("Error al cargar clientes.", {
      toastClassName: "custom-toast-error",
    });
  }
};

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
    if (salesPointFilter.value) {
      url += `&sales_point_id=${salesPointFilter.value}`;
    }
    if (customerFilter.value) {
      url += `&customer_id=${customerFilter.value}`;
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

    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${userStore.token}` },
    });

    const data = response.data;
    if (!data.order_statistics || !data.product_statistics || !data.purchase_statistics) {
      throw new Error("Datos de analítica incompletos");
    }

    analyticsData.value = data;
    isLoaded.value = true;
  } catch (err) {
    error.value = err.message || "Error al cargar analíticas";
    analyticsData.value = null;
    isLoaded.value = false;
    console.error("Fetch analytics error:", err);
    toast.error(error.value, {
      toastClassName: "custom-toast-error",
    });
  } finally {
    loading.value = false;
  }
};

const destroyCharts = () => {
  Object.values(charts.value).forEach(chart => {
    if (chart) {
      chart.destroy();
    }
  });
  charts.value = { sales: null, inventory: null, purchases: null, salesBySalesPoint: null, salesByCustomer: null };
};

const createCharts = () => {
  destroyCharts();

  if (!isLoaded.value || !analyticsData.value) return;

  const salesCanvas = document.getElementById('salesChart');
  if (salesCanvas && analyticsData.value.order_statistics.daily_sales?.length > 0) {
    const salesCtx = salesCanvas.getContext('2d');
    if (salesCtx) {
      charts.value.sales = new Chart(salesCtx, {
        type: chartType.value,
        data: {
          labels: analyticsData.value.order_statistics.daily_sales.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Ingresos Diarios ($)',
            data: analyticsData.value.order_statistics.daily_sales.map(d => d.revenue || 0),
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }, {
            label: 'Órdenes Diarias',
            data: analyticsData.value.order_statistics.daily_sales.map(d => d.orders || 0),
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Ingresos', 'órdenes') } } },
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    }
  }

  const inventoryCanvas = document.getElementById('inventoryChart');
  if (inventoryCanvas && analyticsData.value.product_statistics.daily_stock?.length > 0) {
    const inventoryCtx = inventoryCanvas.getContext('2d');
    if (inventoryCtx) {
      charts.value.inventory = new Chart(inventoryCtx, {
        type: chartType.value,
        data: {
          labels: analyticsData.value.product_statistics.daily_stock.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Cambio Diario en Stock',
            data: analyticsData.value.product_statistics.daily_stock.map(d => d.change || 0),
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: false } },
          plugins: { tooltip: { callbacks: { label: formatTooltip(null, 'unidades') } } },
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    }
  }

  const purchasesCanvas = document.getElementById('purchasesChart');
  if (purchasesCanvas && analyticsData.value.purchase_statistics.daily_purchases?.length > 0) {
    const purchasesCtx = purchasesCanvas.getContext('2d');
    if (purchasesCtx) {
      charts.value.purchases = new Chart(purchasesCtx, {
        type: chartType.value,
        data: {
          labels: analyticsData.value.purchase_statistics.daily_purchases.map(d => new Date(d.day).toLocaleDateString()),
          datasets: [{
            label: 'Costo Diario ($)',
            data: analyticsData.value.purchase_statistics.daily_purchases.map(d => d.cost || 0),
            borderColor: '#9C27B0',
            backgroundColor: 'rgba(156, 39, 176, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }, {
            label: 'Compras Diarias',
            data: analyticsData.value.purchase_statistics.daily_purchases.map(d => d.purchases || 0),
            borderColor: '#673AB7',
            backgroundColor: 'rgba(103, 58, 183, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Costo', 'compras') } } },
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    }
  }

  const salesBySalesPointCanvas = document.getElementById('salesBySalesPointChart');
  if (salesBySalesPointCanvas && analyticsData.value.order_statistics.sales_by_salespoint?.length > 0) {
    const salesBySalesPointCtx = salesBySalesPointCanvas.getContext('2d');
    if (salesBySalesPointCtx) {
      charts.value.salesBySalesPoint = new Chart(salesBySalesPointCtx, {
        type: chartType.value,
        data: {
          labels: analyticsData.value.order_statistics.sales_by_salespoint.map(d => d.items__product__stock_info__sales_point__name),
          datasets: [{
            label: 'Ingresos por Tienda ($)',
            data: analyticsData.value.order_statistics.sales_by_salespoint.map(d => d.total_revenue || 0),
            borderColor: '#FF5722',
            backgroundColor: 'rgba(255, 87, 34, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Ingresos', null) } } },
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    }
  }

  const salesByCustomerCanvas = document.getElementById('salesByCustomerChart');
  if (salesByCustomerCanvas && analyticsData.value.order_statistics.sales_by_customer?.length > 0) {
    const salesByCustomerCtx = salesByCustomerCanvas.getContext('2d');
    if (salesByCustomerCtx) {
      charts.value.salesByCustomer = new Chart(salesByCustomerCtx, {
        type: chartType.value,
        data: {
          labels: analyticsData.value.order_statistics.sales_by_customer.map(d => d.user__username),
          datasets: [{
            label: 'Ingresos por Cliente ($)',
            data: analyticsData.value.order_statistics.sales_by_customer.map(d => d.total_revenue || 0),
            borderColor: '#E91E63',
            backgroundColor: 'rgba(233, 30, 99, 0.2)',
            fill: chartType.value === 'bar' ? true : false,
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } },
          plugins: { tooltip: { callbacks: { label: formatTooltip('Ingresos', null) } } },
          responsive: true,
          maintainAspectRatio: false,
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
      label += context.parsed.y + (unitLabel ? ` ${unitLabel}` : '');
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
  analyticsData.value.order_statistics.sales_by_salespoint.forEach(d => {
    csvData.push(['Ventas por Tienda', `"${d.items__product__stock_info__sales_point__name} - Ingresos"`, d.total_revenue].join(','));
    csvData.push(['Ventas por Tienda', `"${d.items__product__stock_info__sales_point__name} - Órdenes"`, d.total_orders].join(','));
  });
  analyticsData.value.order_statistics.sales_by_customer.forEach(d => {
    csvData.push(['Ventas por Cliente', `"${d.user__username} - Ingresos"`, d.total_revenue].join(','));
    csvData.push(['Ventas por Cliente', `"${d.user__username} - Órdenes"`, d.total_orders].join(','));
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

onMounted(async () => {
  await fetchSalesPointsAndCustomers();
  await updateDashboard();
});

watch([timeFilter, customDateRange, chartType, salesPointFilter, customerFilter], updateDashboard);
</script>

<template>
  <div class="dashboard">
    <h1>Panel de Control</h1>
    <div v-if="loading" class="loading">
      <font-awesome-icon icon="spinner" spin /> Cargando...
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="isLoaded" class="analytics-content">
      <!-- Filter Section -->
      <div class="filter-section">
        <div class="time-filters">
          <button @click="timeFilter = 'day'; customDateRange = [null, null]"
                  :class="{ active: timeFilter === 'day' && !customDateRange[0] }">Día</button>
          <button @click="timeFilter = 'week'; customDateRange = [null, null]"
                  :class="{ active: timeFilter === 'week' && !customDateRange[0] }">Semana</button>
          <button @click="timeFilter = 'month'; customDateRange = [null, null]"
                  :class="{ active: timeFilter === 'month' && !customDateRange[0] }">Mes</button>
          <flat-pickr v-model="customDateRange" :config="{ mode: 'range', dateFormat: 'Y-m-d' }"
                      placeholder="Rango personalizado"></flat-pickr>
        </div>
        <div class="additional-filters">
          <select v-model="salesPointFilter">
            <option :value="null">Todas las Tiendas</option>
            <option v-for="sp in salesPoints" :key="sp.id" :value="sp.id">{{ sp.name }}</option>
          </select>
          <select v-model="customerFilter">
            <option :value="null">Todos los Clientes</option>
            <option v-for="customer in customers" :key="customer.id" :value="customer.id">{{ customer.username }}</option>
          </select>
        </div>
        <div class="chart-type">
          <select v-model="chartType">
            <option value="line">Línea</option>
            <option value="bar">Histograma</option>
          </select>
        </div>
        <button @click="exportToCSV" class="export-button">Exportar a CSV</button>
      </div>

      <!-- Product Statistics -->
      <h2>Estadísticas de Productos</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Total Productos</h4>
          <p>{{ analyticsData.product_statistics.total_products }}</p>
        </div>
        <div class="stat-card">
          <h4>Productos con Stock Bajo</h4>
          <p>{{ analyticsData.product_statistics.low_stock_count }}</p>
        </div>
        <div class="stat-card">
          <h4>Nivel Promedio de Stock</h4>
          <p>{{ analyticsData.product_statistics.avg_stock_level.toFixed(2) }}</p>
        </div>
      </div>
      <div class="chart">
        <h3>Cambio Diario en Stock</h3>
        <div class="chart-container">
          <canvas id="inventoryChart"></canvas>
        </div>
      </div>

      <!-- Order Statistics -->
      <h2>Estadísticas de Pedidos</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Total Pedidos</h4>
          <p>{{ analyticsData.order_statistics.total_orders }}</p>
        </div>
        <div class="stat-card">
          <h4>Ingresos Totales</h4>
          <p>$ {{ analyticsData.order_statistics.total_revenue.toFixed(2) }}</p>
        </div>
      </div>
      <div class="chart">
        <h3>Ventas Diarias</h3>
        <div class="chart-container">
          <canvas id="salesChart"></canvas>
        </div>
      </div>
      <div class="chart">
        <h3>Ingresos por Tienda</h3>
        <div class="chart-container">
          <canvas id="salesBySalesPointChart"></canvas>
        </div>
      </div>
      <div class="chart">
        <h3>Ingresos por Cliente (Top 5)</h3>
        <div class="chart-container">
          <canvas id="salesByCustomerChart"></canvas>
        </div>
      </div>
      <div class="table-wrapper">
        <h3>Productos Más Vendidos</h3>
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>Unidades Vendidas</th>
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

      <!-- Purchase Statistics -->
      <h2>Estadísticas de Compras</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Total Compras</h4>
          <p>{{ analyticsData.purchase_statistics.total_purchases }}</p>
        </div>
        <div class="stat-card">
          <h4>Costo Total</h4>
          <p>$ {{ analyticsData.purchase_statistics.total_purchase_cost.toFixed(2) }}</p>
        </div>
      </div>
      <div class="chart">
        <h3>Compras Diarias</h3>
        <div class="chart-container">
          <canvas id="purchasesChart"></canvas>
        </div>
      </div>
      <div class="table-wrapper">
        <h3>Productos Más Comprados</h3>
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
    <div v-else class="empty-data">Sin datos disponibles</div>
  </div>
</template>

<style scoped>
:root {
  --color-primary: #2563eb;
  --color-secondary: #3b82f6;
  --color-accent: #60a5fa;
  --color-neutral: #ffffff;
  --color-text: #1f2937;
}

.dashboard {
  max-width: 1200px;
  margin: 60px auto 20px;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

h1, h2, h3 {
  color: var(--color-text);
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
}

h2 {
  font-size: 2rem;
  margin: 2rem 0 1rem;
}

h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}

.time-filters {
  display: flex;
  gap: 10px;
}

.time-filters button {
  padding: 8px 16px;
  border: 1px solid #ccc;
  border-radius: 25px;
  cursor: pointer;
  background: #f9f9f9;
  transition: all 0.3s ease;
}

.time-filters button.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.time-filters button:hover:not(.active) {
  background: #e0e0e0;
}

.additional-filters {
  display: flex;
  gap: 10px;
}

.additional-filters select, .chart-type select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 25px;
  background: #f9f9f9;
  cursor: pointer;
}

.additional-filters select:focus, .chart-type select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.chart-type {
  display: flex;
  align-items: center;
}

.export-button {
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.export-button:hover {
  background: var(--color-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card h4 {
  font-size: 1.1rem;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.stat-card p {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
}

.chart {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.chart-container {
  position: relative;
  height: 300px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #f9f9f9;
  border-radius: 10px;
  overflow: hidden;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
}

td {
  color: var(--color-text);
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background: #f0f0f0;
}

.loading, .empty-data {
  text-align: center;
  padding: 2rem;
  color: var(--color-text);
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.error {
  text-align: center;
  padding: 2rem;
  color: #ef4444;
}

:deep(.custom-toast-success) {
  background: var(--gradient-primary);
  border-radius: 10px;
}

:deep(.custom-toast-error) {
  background: linear-gradient(45deg, #ef4444, #f87171);
  border-radius: 10px;
}

@media (max-width: 768px) {
  .dashboard {
    margin: 40px auto 10px;
    padding: 15px;
  }

  h1 {
    font-size: 2rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  h3 {
    font-size: 1.2rem;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .time-filters, .additional-filters {
    justify-content: center;
  }

  .stat-card {
    padding: 0.5rem;
  }

  .stat-card h4 {
    font-size: 1rem;
  }

  .stat-card p {
    font-size: 1.2rem;
  }

  th, td {
    padding: 0.5rem;
    font-size: 0.9rem;
  }

  .chart-container {
    height: 200px;
  }
}
</style>