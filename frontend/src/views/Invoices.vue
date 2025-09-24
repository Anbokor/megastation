<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { useRouter } from 'vue-router';

const invoices = ref([]);
const loading = ref(true);
const toast = useToast();
const router = useRouter();

// Filter states
const searchQuery = ref('');
const statusFilter = ref('');

// This function will fetch invoices from the backend.
onMounted(async () => {
  try {
    const response = await axios.get('/api/purchases/invoices/');
    invoices.value = response.data;
  } catch (error) {
    toast.error('Error al cargar las facturas.');
    console.error('Failed to fetch invoices:', error);
  } finally {
    loading.value = false;
  }
});

// Computed property to filter invoices based on search and status
const filteredInvoices = computed(() => {
  let filtered = invoices.value;

  // Apply search query
  if (searchQuery.value) {
    const lowerCaseQuery = searchQuery.value.toLowerCase();
    filtered = filtered.filter(invoice => 
      invoice.invoice_number.toLowerCase().includes(lowerCaseQuery) ||
      invoice.supplier.toLowerCase().includes(lowerCaseQuery)
    );
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(invoice => invoice.status === statusFilter.value);
  }

  return filtered;
});

const goToCreateInvoice = () => {
  router.push('/invoices/create');
};

// Navigate to the detail page for an invoice
const goToInvoiceDetail = (invoiceId) => {
  router.push(`/invoices/${invoiceId}`);
};

// Helper to format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric', month: 'short', day: 'numeric'
  });
};
</script>

<template>
  <div class="invoices-container">
    <div class="invoices-header">
      <h1>Gestión de Facturas de Compra</h1>
      <button @click="goToCreateInvoice" class="create-btn">
        <font-awesome-icon icon="plus" /> Crear Factura
      </button>
    </div>

    <!-- Filter section -->
    <div class="filters">
      <input type="text" v-model="searchQuery" placeholder="Buscar por Nº o proveedor..." class="search-input" />
      <select v-model="statusFilter" class="status-select">
        <option value="">Todos los estados</option>
        <option value="pendiente">Pendiente</option>
        <option value="procesada">Procesada</option>
        <option value="anulada">Anulada</option>
      </select>
    </div>

    <div v-if="loading" class="loading-spinner">
      <font-awesome-icon icon="spinner" spin size="3x" />
      <p>Cargando facturas...</p>
    </div>
    <div v-else-if="filteredInvoices.length > 0" class="invoices-list">
      <!-- Added a header for the list -->
      <div class="invoice-item-header">
        <div>Nº Factura</div>
        <div>Proveedor</div>
        <div>Fecha</div>
        <div>Estado</div>
        <div>Total</div>
      </div>
      <div 
        v-for="invoice in filteredInvoices" 
        :key="invoice.id" 
        class="invoice-item" 
        @click="goToInvoiceDetail(invoice.id)"
        title="Ver detalles de la factura"
      >
        <span>{{ invoice.invoice_number }}</span>
        <span>{{ invoice.supplier }}</span>
        <span>{{ formatDate(invoice.created_at) }}</span>
        <span>{{ invoice.status }}</span>
        <span>${{ invoice.total_cost }}</span>
      </div>
    </div>
    <div v-else class="no-invoices">
      <p>No se encontraron facturas que coincidan con los filtros.</p>
    </div>
  </div>
</template>

<style scoped>
.invoices-container { max-width: 1000px; margin: 40px auto; padding: 30px; background: var(--color-neutral); border-radius: 15px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); }
.invoices-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.create-btn { background-color: var(--color-primary); color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; transition: background-color 0.3s ease; }
.create-btn:hover { background-color: var(--color-primary-dark); }

.filters { display: flex; gap: 15px; margin-bottom: 20px; }
.search-input, .status-select { padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
.search-input { flex-grow: 1; }

.loading-spinner, .no-invoices { text-align: center; padding: 40px; color: var(--color-text-muted); }

/* Using grid for better alignment */
.invoice-item-header, .invoice-item {
  display: grid;
  grid-template-columns: 1.5fr 2fr 1fr 1fr 1fr;
  gap: 15px;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
}

.invoice-item-header {
  font-weight: bold;
  background-color: #f8f9fa;
}

.invoice-item {
  background-color: #f9f9f9;
  border-left: 5px solid var(--color-primary);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.invoice-item:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
</style>
