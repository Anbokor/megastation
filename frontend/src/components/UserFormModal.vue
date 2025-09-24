<script setup>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const props = defineProps({
  show: Boolean,
  user: Object, // Pass a user object for editing, null for creating
});

const emit = defineEmits(['close', 'user-saved']);

const toast = useToast();
const formData = ref({});
const salesPoints = ref([]);
const loading = ref(false);

const roles = ['admin', 'store_admin', 'seller', 'customer'];

// Fetch sales points for the dropdown
onMounted(async () => {
  try {
    const response = await axios.get('/api/inventory/sales-points/');
    salesPoints.value = response.data;
  } catch (error) {
    toast.error('No se pudieron cargar los puntos de venta.');
  }
});

// Watch for the user prop to change and populate the form
watch(() => props.user, (newUser) => {
  if (newUser) {
    formData.value = { ...newUser };
  } else {
    formData.value = {
      username: '',
      email: '',
      password: '',
      role: 'customer',
      sales_point: null,
      is_active: true,
    };
  }
}, { immediate: true });

const isStaffRole = (role) => {
  return ['store_admin', 'seller'].includes(role);
};

const submitForm = async () => {
  loading.value = true;
  try {
    let response;
    const payload = { ...formData.value };

    if (props.user && props.user.id) {
      // Update existing user
      response = await axios.patch(`/api/users/${props.user.id}/`, payload);
    } else {
      // Create new user
      response = await axios.post('/api/users/', payload);
    }
    
    toast.success(`Usuario ${props.user ? 'actualizado' : 'creado'} con éxito.`);
    emit('user-saved', response.data);
    emit('close');

  } catch (error) {
    const errorMessage = Object.values(error.response.data).flat().join(' ');
    toast.error(errorMessage || 'Ocurrió un error.');
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <h2>{{ user ? 'Editar Usuario' : 'Crear Nuevo Usuario' }}</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>Username</label>
          <input v-model="formData.username" type="text" required />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="formData.email" type="email" required />
        </div>
        <div class="form-group">
          <label>Contraseña {{ user ? '(Dejar en blanco para no cambiar)' : '' }}</label>
          <input v-model="formData.password" type="password" :required="!user" />
        </div>
        <div class="form-group">
          <label>Rol</label>
          <select v-model="formData.role">
            <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
          </select>
        </div>
        <div v-if="isStaffRole(formData.role)" class="form-group">
          <label>Punto de Venta</label>
          <select v-model="formData.sales_point">
            <option :value="null">Ninguno</option>
            <option v-for="point in salesPoints" :key="point.id" :value="point.id">{{ point.name }}</option>
          </select>
        </div>
        <div class="form-group-checkbox">
          <label>Activo</label>
          <input v-model="formData.is_active" type="checkbox" />
        </div>
        <div class="form-actions">
          <button type="button" @click="emit('close')" class="cancel-btn">Cancelar</button>
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 30px; border-radius: 10px; width: 90%; max-width: 500px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
.form-group-checkbox { display: flex; align-items: center; gap: 10px; }
.form-actions { display: flex; justify-content: flex-end; gap: 15px; margin-top: 20px; }
.cancel-btn, .submit-btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; }
.cancel-btn { background-color: #f0f0f0; }
.submit-btn { background-color: var(--color-primary); color: white; }
</style>
