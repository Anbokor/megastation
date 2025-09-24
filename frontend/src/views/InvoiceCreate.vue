<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import axios from 'axios';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const router = useRouter();
const toast = useToast();

const invoice = ref({
  invoice_number: '',
  supplier: '',
  sales_point: null,
  items: [{ product: null, quantity: 1, cost_per_item: '' }],
});

const salesPoints = ref([]);
const products = ref([]);
const loading = ref(false);
const dataLoading = ref(true);

const totalInvoiceAmount = computed(() => {
  return invoice.value.items.reduce((total, item) => {
    const cost = parseFloat(String(item.cost_per_item).replace(',', '.')) || 0;
    const quantity = parseInt(item.quantity, 10) || 0;
    return total + (cost * quantity);
  }, 0).toFixed(2);
});

onMounted(async () => {
  try {
    const [salesPointsRes, productsRes] = await Promise.all([
      axios.get('/api/inventory/sales-points/'),
      axios.get('/api/store/products/')
    ]);
    salesPoints.value = salesPointsRes.data;
    products.value = productsRes.data;
  } catch (error) {
    toast.error('Error al cargar los datos necesarios para el formulario.');
  } finally {
    dataLoading.value = false;
  }
});

const addItem = () => {
  invoice.value.items.push({ product: null, quantity: 1, cost_per_item: '' });
};

const removeItem = (index) => {
  if (invoice.value.items.length > 1) {
    invoice.value.items.splice(index, 1);
  }
};

const validateForm = () => {
  for (const item of invoice.value.items) {
    if (!item.product) {
      toast.error('Todos los artículos deben tener un producto seleccionado.');
      return false;
    }
    const costRegex = /^[+]?([0-9]+([.,][0-9]{1,2})?|[.,][0-9]{1,2})$/;
    if (!costRegex.test(item.cost_per_item) || parseFloat(String(item.cost_per_item).replace(',', '.')) <= 0) {
        toast.error(`El costo por unidad (${item.cost_per_item}) es inválido. Debe ser un número positivo.`);
        return false;
    }
    const quantity = parseInt(item.quantity, 10);
    if (isNaN(quantity) || quantity <= 0) {
      toast.error(`La cantidad para el producto seleccionado debe ser un número mayor que cero.`);
      return false;
    }
  }
  return true;
};

const submitForm = async () => {
  if (!validateForm()) {
    return;
  }

  loading.value = true;
  try {
    const payload = {
      invoice_number: invoice.value.invoice_number,
      supplier: invoice.value.supplier,
      sales_point: invoice.value.sales_point,
      items: invoice.value.items.map(item => ({
        product_id: item.product,
        quantity: parseInt(item.quantity, 10),
        // THE FINAL, CORRECT FIX: The backend view expects 'purchase_price', not 'cost_per_item'.
        purchase_price: String(item.cost_per_item).replace(',', '.'),
      })),
    };

    await axios.post('/api/purchases/invoices/create/', payload);
    
    toast.success('Factura creada con éxito.');
    router.push('/invoices');

  } catch (error) {
    const errorMessage = error.response?.data?.error || 'Error al crear la factura.';
    toast.error(errorMessage);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="invoice-create-container">
    <h1>Crear Nueva Factura de Compra</h1>
    <div v-if="dataLoading" class="loading-spinner">
      <p>Cargando datos...</p>
    </div>
    <form v-else @submit.prevent="submitForm" class="invoice-form">
      <div class="form-section">
        <h2>Detalles Generales</h2>
        <div class="form-group">
          <label>Número de Factura (opcional)</label>
          <input v-model="invoice.invoice_number" type="text" placeholder="Dejar en blanco para auto-generar" />
        </div>
        <div class="form-group">
          <label>Proveedor</label>
          <input v-model="invoice.supplier" type="text" placeholder="Nombre del proveedor" required />
        </div>
        <div class="form-group">
          <label>Punto de Venta</label>
          <select v-model="invoice.sales_point" required>
            <option :value="null" disabled>Seleccione un punto de venta</option>
            <option v-for="point in salesPoints" :key="point.id" :value="point.id">
              {{ point.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="form-section">
        <h2>Artículos de la Factura</h2>
        <div v-for="(item, index) in invoice.items" :key="index" class="invoice-item-row">
          <div class="form-group product-selector">
            <label>Producto</label>
            <v-select
              v-model="item.product"
              :options="products"
              :reduce="product => product.id"
              label="name"
              placeholder="Buscar y seleccionar un producto"
            ></v-select>
          </div>
          <div class="form-group">
            <label>Cantidad</label>
            <input v-model="item.quantity" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Costo por Unidad</label>
            <input v-model="item.cost_per_item" type="text" placeholder="0.00" />
          </div>
          <button type="button" @click="removeItem(index)" class="remove-item-btn" :disabled="invoice.items.length <= 1">
            <font-awesome-icon icon="trash" />
          </button>
        </div>
        <button type="button" @click="addItem" class="add-item-btn">Añadir Artículo</button>
      </div>
      
      <div class="form-summary">
        <h3>Total de la Factura: ARS {{ totalInvoiceAmount }}</h3>
      </div>

      <div class="form-actions">
        <button type="button" @click="router.push('/invoices')" class="cancel-btn">Cancelar</button>
        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? 'Guardando...' : 'Guardar Factura' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.invoice-create-container { max-width: 900px; margin: 40px auto; padding: 30px; background: #fff; border-radius: 15px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); }
.invoice-form { display: flex; flex-direction: column; gap: 20px; }
.form-section { padding: 20px; border: 1px solid #eee; border-radius: 8px; }
.form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 1rem; }
.form-group label { font-weight: 500; }
.form-group input, .form-group select { padding: 10px; border-radius: 5px; border: 1px solid #ccc; width: 100%; }
.invoice-item-row { display: grid; grid-template-columns: 3fr 1fr 1fr auto; gap: 15px; align-items: flex-end; margin-bottom: 15px; }
.add-item-btn { background-color: #3498db; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; margin-top: 10px; width: fit-content; }
.remove-item-btn { background-color: #e74c3c; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; height: fit-content; }
.remove-item-btn:disabled { background-color: #ccc; }
.form-summary { padding: 20px; background-color: #f8f9fa; text-align: right; border-top: 2px solid #3498db; }
.form-summary h3 { margin: 0; font-size: 1.5em; }
.form-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 20px; }
.cancel-btn, .submit-btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; }
.cancel-btn { background-color: #f0f0f0; }
.submit-btn { background-color: #28a745; color: white; }
.submit-btn:disabled { background-color: #b0b0b0; }
.loading-spinner { text-align: center; padding: 40px; }
.product-selector .vs__dropdown-toggle { padding: 6px; border-radius: 5px; border: 1px solid #ccc; }
</style>
