<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const invoice = ref(null);
const loading = ref(true);
const selectedStatus = ref('');

// The available statuses for an invoice
const availableStatuses = ['pendiente', 'procesada', 'anulada'];

// Fetch invoice details based on the ID from the URL
onMounted(async () => {
  const invoiceId = route.params.id;
  try {
    const response = await axios.get(`/api/purchases/invoices/${invoiceId}/`);
    invoice.value = response.data;
    // Initialize the dropdown with the current status
    selectedStatus.value = invoice.value.status;
  } catch (error) {
    toast.error('Error al cargar los detalles de la factura.');
    router.push('/invoices');
  } finally {
    loading.value = false;
  }
});

// Function to update the invoice status
const updateStatus = async () => {
  if (selectedStatus.value === invoice.value.status) {
    toast.info('El estado seleccionado es el actual.');
    return;
  }

  loading.value = true;
  try {
    const response = await axios.put(`/api/purchases/invoices/${invoice.value.id}/status/`, {
      status: selectedStatus.value
    });
    invoice.value = response.data;
    selectedStatus.value = invoice.value.status;
    toast.success('Estado de la factura actualizado con éxito.');
  } catch (error) {
    toast.error(error.response?.data?.error || 'Error al actualizar el estado.');
    // Revert dropdown to original status on failure
    selectedStatus.value = invoice.value.status;
  } finally {
    loading.value = false;
  }
};

</script>

<template>
  <div class="invoice-detail-container">
    <div v-if="loading" class="loading-spinner">
      <font-awesome-icon icon="spinner" spin size="3x" />
      <p>Cargando detalles...</p>
    </div>
    <div v-else-if="invoice" class="invoice-card">
      <div class="card-header">
        <h1>Factura Nº: {{ invoice.invoice_number }}</h1>
        <button @click="router.push('/invoices')" class="back-btn">Volver a la lista</button>
      </div>
      <div class="card-body">
        <div class="details-grid">
          <div><strong>Proveedor:</strong> {{ invoice.supplier }}</div>
          <div><strong>Punto de Venta:</strong> {{ invoice.sales_point.name }}</div>
          <div><strong>Creado por:</strong> {{ invoice.user?.username || 'N/A' }}</div>
          <div><strong>Fecha:</strong> {{ new Date(invoice.created_at).toLocaleDateString() }}</div>
          <div><strong>Estado:</strong> <span :class="`status-${invoice.status}`">{{ invoice.status }}</span></div>
          <div><strong>Costo Total:</strong> <span class="total-cost">ARS {{ Number(invoice.total_cost).toFixed(2) }}</span></div>
        </div>

        <!-- Status Management Section -->
        <div class="status-management-section">
          <h2>Gestionar Estado</h2>
          <div class="status-controls">
            <select v-model="selectedStatus">
              <option v-for="status in availableStatuses" :key="status" :value="status">
                {{ status }}
              </option>
            </select>
            <button @click="updateStatus" :disabled="loading || selectedStatus === invoice.status">
              Actualizar Estado
            </button>
          </div>
        </div>
        
        <div class="items-section">
          <h2>Artículos</h2>
          <div class="items-list">
            <div class="item-header">
              <div>Producto</div>
              <div>Cantidad</div>
              <div>Costo Unitario</div>
              <div>Subtotal</div>
            </div>
            <div v-for="item in invoice.items" :key="item.id" class="item-row">
              <div>{{ item.product.name }}</div>
              <div>{{ item.quantity }}</div>
              <div>ARS {{ Number(item.cost_per_item).toFixed(2) }}</div>
              <div>ARS {{ (item.quantity * Number(item.cost_per_item)).toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.invoice-detail-container { max-width: 1000px; margin: 40px auto; }
.loading-spinner { text-align: center; padding: 50px; }
.invoice-card { background: var(--color-neutral); border-radius: 15px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); overflow: hidden; }
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; background-color: #f8f9fa; border-bottom: 1px solid #eee; }
.card-header h1 { margin: 0; font-size: 1.5em; }
.back-btn { background: none; border: 1px solid #ccc; padding: 8px 15px; border-radius: 5px; cursor: pointer; }
.card-body { padding: 20px; }
.details-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 30px; }
.details-grid div { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }
.total-cost { font-weight: bold; color: var(--color-primary); }
.items-section h2 { margin-bottom: 15px; }
.items-list .item-header, .items-list .item-row { display: grid; grid-template-columns: 3fr 1fr 1fr 1fr; gap: 10px; padding: 10px; border-bottom: 1px solid #eee; }
.items-list .item-header { font-weight: bold; background-color: #f2f2f2; }
.status-procesada { color: green; font-weight: bold; }
.status-pendiente { color: orange; font-weight: bold; }
.status-anulada { color: red; font-weight: bold; }

/* New styles for status management */
.status-management-section { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
.status-controls { display: flex; align-items: center; gap: 15px; }
.status-controls select { padding: 8px; border-radius: 5px; border: 1px solid #ccc; }
.status-controls button { background-color: var(--color-secondary); color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; }
.status-controls button:disabled { background-color: #ccc; cursor: not-allowed; }
</style>
