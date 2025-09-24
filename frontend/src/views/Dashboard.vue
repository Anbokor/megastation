<script setup>
import { ref, onMounted, watch, nextTick, computed } from "vue";
import { useUserStore } from "@/store/user";
import { useToast } from "vue-toastification";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import FlatPickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";

Chart.register(...registerables);

// --- STATE MANAGEMENT ---
const userStore = useUserStore();
const toast = useToast();
const loading = ref(true);
const error = ref(null);
const analyticsData = ref(null);
const charts = ref({});

// --- FILTERS ---
const timeFilter = ref('month');
const customDateRange = ref([]);
const salesPointFilter = ref(null);
const salesPoints = ref([]);

// --- COMPUTED KPIS ---
const kpis = computed(() => {
  const defaults = {
    total_revenue: 0,
    total_cost_of_goods_sold: 0, // Новое поле: себестоимость проданных товаров
    net_profit: 0,
    profit_margin: 0,
    total_orders: 0,
    avg_order_value: 0,
    low_stock_count: 0,
    total_purchase_cost: 0, // Новое поле: общая сумма закупок
  };
  if (!analyticsData.value?.kpis) return defaults;
  return { ...defaults, ...analyticsData.value.kpis };
});

// --- DATA FETCHING ---
const fetchInitialData = async () => {
  // FIX: Removed userStore.isStaff check. The backend will handle role permissions.
  if (!userStore.isAuthenticated) return;
  try {
    const res = await axios.get("/api/inventory/sales-points/");
    salesPoints.value = res.data;
  } catch (err) {
    toast.error("Error al cargar los puntos de venta.");
  }
};

const fetchAnalytics = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = new URLSearchParams();
    if (customDateRange.value && customDateRange.value.length === 2) {
      params.append('start_date', customDateRange.value[0]);
      params.append('end_date', customDateRange.value[1]);
    } else {
      params.append('time_filter', timeFilter.value);
    }
    if (salesPointFilter.value) {
      params.append('sales_point_id', salesPointFilter.value);
    }
    const response = await axios.get(`/api/analytics/?${params.toString()}`);
    analyticsData.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.error || "Error cargando analíticas.";
    toast.error(error.value);
  } finally {
    loading.value = false;
    await nextTick();
    renderAllCharts();
  }
};

// --- CHARTING ---
const destroyCharts = () => {
  Object.values(charts.value).forEach(chart => chart?.destroy());
  charts.value = {};
};

const renderAllCharts = () => {
  destroyCharts();
  if (!analyticsData.value) return;

  renderMainChart();
  renderTopProductsChart();
};

const renderMainChart = () => {
  const salesData = analyticsData.value.time_series?.sales || [];
  const purchasesData = analyticsData.value.time_series?.purchases || [];
  const profitData = analyticsData.value.time_series?.profit || []; // Новые данные о прибыли

  if (!salesData.length && !purchasesData.length) return;

  const allDates = [...new Set([
    ...salesData.map(d => d.day),
    ...purchasesData.map(d => d.day),
    ...profitData.map(d => d.day)
  ])].sort();

  const labels = allDates.map(date => new Date(date).toLocaleDateString());

  const salesByDate = new Map(salesData.map(d => [d.day, d.revenue]));
  const purchasesByDate = new Map(purchasesData.map(d => [d.day, d.cost]));
  const profitByDate = new Map(profitData.map(d => [d.day, d.profit]));

  const revenueDataset = allDates.map(date => salesByDate.get(date) || 0);
  const costDataset = allDates.map(date => purchasesByDate.get(date) || 0);
  const profitDataset = allDates.map(date => profitByDate.get(date) || 0);

  createChart('mainChart', 'line', labels, [
    {
      label: 'Ingresos',
      data: revenueDataset,
      borderColor: '#4ade80',
      backgroundColor: 'rgba(74, 222, 128, 0.1)',
      fill: true,
      tension: 0.4,
      yAxisID: 'y',
    },
    {
      label: 'Costos',
      data: costDataset,
      borderColor: '#f87171',
      backgroundColor: 'rgba(248, 113, 113, 0.1)',
      fill: true,
      tension: 0.4,
      yAxisID: 'y',
    },
    {
      label: 'Ganancia',
      data: profitDataset,
      borderColor: '#60a5fa',
      backgroundColor: 'rgba(96, 165, 250, 0.1)',
      fill: true,
      tension: 0.4,
      yAxisID: 'y',
    }
  ], {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { 
      title: { display: true, text: 'Rendimiento Financiero (Ingresos, Costos y Ganancia)', color: 'var(--color-text-primary)', font: { size: 16 } },
      legend: { display: true, position: 'top' }
    },
    scales: { 
      x: { ticks: { color: 'var(--color-text-secondary)' }, grid: { color: 'var(--color-border)' } }, 
      y: { type: 'linear', position: 'left', ticks: { color: 'var(--color-text-secondary)' }, grid: { color: 'var(--color-border)' } }
    }
  });
};

const renderTopProductsChart = () => {
  const topProfitableProducts = analyticsData.value.top_lists?.profitable_products || [];
  if (!topProfitableProducts.length) return;

  createChart('topProductsChart', 'bar', 
    topProfitableProducts.map(p => p.product__name),
    [{
      label: 'Ganancia Total',
      data: topProfitableProducts.map(p => p.total_profit),
      backgroundColor: '#60a5fa',
      borderRadius: 4,
    }],
    {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        title: { display: true, text: 'Top 5 Productos más Rentables', color: 'var(--color-text-primary)', font: { size: 16 } },
        legend: { display: false }
      },
      scales: { 
        x: { ticks: { color: 'var(--color-text-secondary)' }, grid: { color: 'var(--color-border)' } }, 
        y: { ticks: { color: 'var(--color-text-secondary)' }, grid: { display: false } }
      }
    }
  );
};

const createChart = (canvasId, type, labels, datasets, options) => {
  const canvas = document.getElementById(canvasId);
  if (canvas) {
    charts.value[canvasId] = new Chart(canvas.getContext('2d'), { type, data: { labels, datasets }, options });
  }
};

// --- LIFECYCLE & WATCHERS ---
onMounted(() => {
  fetchInitialData();
  fetchAnalytics();
});

watch([timeFilter, customDateRange, salesPointFilter], fetchAnalytics, { deep: true });

</script>

<template>
  <div class="dashboard-page">
    <h1>Panel de Control</h1>

    <!-- Filters -->
    <div class="dashboard-filters card">
      <div class="time-filters">
        <button @click="timeFilter = 'day'; customDateRange = []" :class="{ active: timeFilter === 'day' }">Hoy</button>
        <button @click="timeFilter = 'week'; customDateRange = []" :class="{ active: timeFilter === 'week' }">7 Días</button>
        <button @click="timeFilter = 'month'; customDateRange = []" :class="{ active: timeFilter === 'month' }">30 Días</button>
        <flat-pickr v-model="customDateRange" :config="{ mode: 'range', dateFormat: 'Y-m-d' }" @on-change="timeFilter=''" placeholder="Rango personalizado"></flat-pickr>
      </div>
      <div class="additional-filters">
        <select v-model="salesPointFilter">
          <option :value="null">Todas las Tiendas</option>
          <option v-for="sp in salesPoints" :key="sp.id" :value="sp.id">{{ sp.name }}</option>
        </select>
      </div>
    </div>

    <!-- Main Content -->
    <div v-if="loading" class="loading-state">Cargando...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <div v-else-if="analyticsData" class="dashboard-content">
      <!-- KPI Grid -->
      <div class="kpi-grid">
        <div class="kpi-card highlight">
          <h4>Beneficio Neto</h4>
          <p :class="kpis.net_profit >= 0 ? 'text-profit' : 'text-loss'">
            ARS {{ kpis.net_profit.toFixed(2) }}
            <span class="percentage" v-if="kpis.profit_margin">({{ kpis.profit_margin.toFixed(1) }}%)</span>
          </p>
        </div>
        <div class="kpi-card">
          <h4>Ingresos</h4>
          <p class="text-revenue">ARS {{ kpis.total_revenue.toFixed(2) }}</p>
        </div>
        <div class="kpi-card">
          <h4>Costo de Mercadería Vendida</h4>
          <p class="text-cost">ARS {{ kpis.total_cost_of_goods_sold.toFixed(2) }}</p>
        </div>
        <div class="kpi-card">
          <h4>Compras durante el período</h4>
          <p class="text-purchase">ARS {{ kpis.total_purchase_cost.toFixed(2) }}</p>
        </div>
        <div class="kpi-card">
          <h4>Ticket Promedio</h4>
          <p>ARS {{ kpis.avg_order_value.toFixed(2) }}</p>
        </div>
        <div class="kpi-card warning" v-if="kpis.low_stock_count">
          <h4>Productos con stock bajo</h4>
          <p class="text-warning">{{ kpis.low_stock_count }}</p>
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <div class="chart-card main-chart">
          <div class="chart-container">
            <canvas id="mainChart"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <div class="chart-container">
            <canvas id="topProductsChart"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <h3>Top Clientes por Ingresos</h3>
          <div v-if="analyticsData.top_lists?.customers?.length" class="top-list">
            <ul>
              <li v-for="customer in analyticsData.top_lists.customers" :key="customer.order__user__username">
                <span>{{ customer.order__user__username }}</span>
                <strong>ARS {{ customer.total_revenue.toFixed(2) }}</strong>
              </li>
            </ul>
          </div>
        </div>
        <div class="chart-card">
          <h3>Top Productos más Vendidos</h3>
          <div v-if="analyticsData.top_lists?.sold_products?.length" class="top-list">
            <ul>
              <li v-for="product in analyticsData.top_lists.sold_products" :key="product.product__name">
                <span>{{ product.product__name }}</span>
                <strong>{{ product.total_quantity }} unidades</strong>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Добавляем новые стили */
.kpi-card.highlight {
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-accent) 100%);
  border: 1px solid var(--color-border-accent);
}

.kpi-card.warning {
  border: 1px solid var(--warning-color);
}

.kpi-card .percentage {
  font-size: 1rem;
  opacity: 0.8;
  margin-left: 0.5rem;
}

.text-purchase {
  color: var(--purchase-color);
}

.text-warning {
  color: var(--warning-color);
}

/* Обновляем переменные цветов */
:root {
  --profit-color: #22c55e;
  --loss-color: #ef4444;
  --revenue-color: #3b82f6;
  --cost-color: #f97316;
  --purchase-color: #8b5cf6;
  --warning-color: #eab308;
  --color-surface-accent: rgba(59, 130, 246, 0.1);
  --color-border-accent: rgba(59, 130, 246, 0.2);
}

.dashboard-page { display: flex; flex-direction: column; gap: 1.5rem; }

.card { background-color: var(--color-surface); border-radius: 0.75rem; box-shadow: var(--shadow-sm); }

.dashboard-filters { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; justify-content: space-between; padding: 1rem; }
.time-filters, .additional-filters { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }
.time-filters button, .dashboard-filters select, .dashboard-filters .flatpickr-input { padding: 0.5rem 1rem; border: 1px solid var(--color-border); border-radius: 0.5rem; background-color: var(--color-surface); color: var(--color-text-primary); font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.time-filters button:hover, .dashboard-filters select:hover { border-color: var(--color-primary); }
.time-filters button.active { background-color: var(--color-primary); color: white; border-color: var(--color-primary); }

.loading-state, .error-state { text-align: center; padding: 4rem; font-size: 1.2rem; color: var(--color-text-secondary); }
.error-state { color: var(--loss-color); }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; }
.kpi-card { background: var(--color-surface); padding: 1.5rem; border-radius: 0.75rem; box-shadow: var(--shadow-sm); }
.kpi-card h4 { margin: 0 0 0.5rem; color: var(--color-text-secondary); font-size: 0.9rem; font-weight: 500; }
.kpi-card p { margin: 0; font-size: 1.75rem; font-weight: 700; }
.kpi-card .text-profit { color: var(--profit-color); }
.kpi-card .text-loss { color: var(--loss-color); }
.kpi-card .text-revenue { color: var(--revenue-color); }
.kpi-card .text-cost { color: var(--cost-color); }

.charts-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-top: 1.5rem; }
.chart-card { background: var(--color-surface); padding: 1.5rem; border-radius: 0.75rem; box-shadow: var(--shadow-sm); min-height: 350px; display: flex; flex-direction: column; }
.chart-container { position: relative; flex-grow: 1; }
.no-data { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--color-text-secondary); }
.no-data-table { padding: 2rem; text-align: center; color: var(--color-text-secondary); }

.top-list h3 { margin-top: 0; margin-bottom: 1rem; }
.top-list ul { list-style: none; padding: 0; margin: 0; }
.top-list li { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border); }
.top-list li:last-child { border-bottom: none; }
.top-list li strong { font-weight: 600; }

@media (min-width: 1024px) {
  .charts-grid { grid-template-columns: repeat(3, 1fr); }
  .main-chart { grid-column: 1 / 4; height: 450px; }
  .secondary-chart { min-height: 400px; }
}

@media (min-width: 1280px) {
  .charts-grid { grid-template-columns: 2fr 1fr; }
  .main-chart { grid-column: 1 / 2; grid-row: 1 / 3; height: auto; }
  .secondary-chart { grid-column: 2 / 3; }
}
</style>
