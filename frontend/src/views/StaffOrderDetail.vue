<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const order = ref(null);
const loading = ref(true);
const error = ref(null);
const selectedStatus = ref('');

const orderId = route.params.id;

const availableStatuses = [
    'pendiente',
    'en_proceso',
    'enviado',
    'completado',
    'cancelado',
    'fallido'
];

const fetchOrder = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await axios.get(`/api/orders/staff/${orderId}/`);
        order.value = response.data;
        selectedStatus.value = order.value.status;
    } catch (err) {
        error.value = 'Error al cargar el pedido.';
        toast.error(error.value);
        console.error(err);
    } finally {
        loading.value = false;
    }
};

const updateStatus = async () => {
    if (!selectedStatus.value || selectedStatus.value === order.value.status) {
        toast.info('No hay cambios en el estado.');
        return;
    }
    loading.value = true;
    try {
        const response = await axios.put(`/api/orders/staff/${orderId}/`, {
            status: selectedStatus.value
        });
        order.value = response.data;
        selectedStatus.value = order.value.status;
        toast.success('¡Estado del pedido actualizado con éxito!');
    } catch (err) {
        const errorMessage = err.response?.data?.error || 'Error al actualizar el estado.';
        toast.error(errorMessage);
        console.error(err);
        selectedStatus.value = order.value.status;
    } finally {
        loading.value = false;
    }
};

const getStatusClass = (status) => {
    return `status-${status}`;
};

onMounted(fetchOrder);

</script>

<template>
    <div class="staff-order-detail-page">
        <div v-if="loading" class="loading-state">Cargando...</div>
        <div v-else-if="error" class="error-state">{{ error }}</div>
        <div v-else-if="order" class="order-details-container card">
            <h1 class="page-title">Detalle del Pedido #{{ order.id }}</h1>

            <div class="order-summary">
                <div class="summary-item">
                    <strong>Cliente:</strong> {{ order.user.username }} ({{ order.user.email || 'N/A' }})
                </div>
                <div class="summary-item">
                    <strong>Fecha:</strong> {{ new Date(order.created_at).toLocaleString() }}
                </div>
                <div class="summary-item">
                    <strong>Método de Pago:</strong> {{ order.payment_method_display }}
                </div>
                <div class="summary-item">
                    <strong>Estado Actual:</strong>
                    <span :class="['status-badge', getStatusClass(order.status)]">{{ order.status_display }}</span>
                </div>
            </div>

            <div class="status-management">
                <h3>Gestionar Estado</h3>
                <div class="status-update-form">
                    <select v-model="selectedStatus">
                        <option v-for="status in availableStatuses" :key="status" :value="status">
                            {{ status }}
                        </option>
                    </select>
                    <button @click="updateStatus" :disabled="loading || selectedStatus === order.status" class="btn btn-primary">
                        Actualizar Estado
                    </button>
                </div>
            </div>

            <div class="order-items">
                <h3>Artículos del Pedido</h3>
                <ul>
                    <li v-for="item in order.items" :key="item.id" class="order-item">
                        <img :src="item.product.image_url" :alt="item.product.name" class="item-image"/>
                        <div class="item-info">
                            <span class="item-name">{{ item.product.name }}</span>
                            <span class="item-quantity">Cantidad: {{ item.quantity }}</span>
                        </div>
                        <div class="item-price">
                            <!-- THE FINAL FIX: Use item.price which is correctly sent by the backend -->
                            <span>Precio Unit.: ARS {{ Number(item.price).toFixed(2) }}</span>
                            <strong>Subtotal: ARS {{ (Number(item.price) * item.quantity).toFixed(2) }}</strong>
                        </div>
                    </li>
                </ul>
            </div>

            <div class="order-total">
                <strong>Total del Pedido: ARS {{ Number(order.total_price).toFixed(2) }}</strong>
            </div>
        </div>
    </div>
</template>

<style scoped>
.staff-order-detail-page {
    max-width: 900px;
    margin: 40px auto;
    padding: 2rem;
}
.card {
    background-color: var(--color-surface);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-md);
    padding: 2rem;
}
.page-title {
    margin-bottom: 2rem;
    text-align: center;
}
.order-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
}
.summary-item {
    font-size: 1rem;
}
.status-management {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background-color: var(--color-background);
    border-radius: var(--border-radius-md);
}
.status-update-form {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.status-update-form select {
    padding: 0.5rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    flex-grow: 1;
}
.order-items ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
.order-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid var(--color-border);
}
.order-item:last-child {
    border-bottom: none;
}
.item-image {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: var(--border-radius-sm);
}
.item-info {
    flex-grow: 1;
}
.item-name {
    font-weight: 600;
    display: block;
}
.item-price {
    text-align: right;
}
.item-price span {
    display: block;
    font-size: 0.9rem;
    color: var(--color-text-secondary);
}
.order-total {
    text-align: right;
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border-accent);
    color: var(--color-primary);
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
.status-completado { background-color: #22c55e; }
.status-cancelado { background-color: #71717a; }
.status-fallido { background-color: #ef4444; }
</style>
