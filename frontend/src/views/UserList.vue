<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import UserFormModal from '@/components/UserFormModal.vue'; // Import the modal component

const users = ref([]);
const loading = ref(true);
const toast = useToast();

const searchQuery = ref('');

// Modal state
const isModalOpen = ref(false);
const selectedUser = ref(null); // For editing

// Fetch users from the backend
onMounted(async () => {
  await fetchUsers();
});

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/users/');
    users.value = response.data;
  } catch (error) {
    toast.error('Error al cargar la lista de usuarios.');
    console.error('Failed to fetch users:', error);
  } finally {
    loading.value = false;
  }
};

// Computed property to filter users
const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return users.value;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return users.value.filter(user =>
    user.username.toLowerCase().includes(lowerCaseQuery) ||
    user.email.toLowerCase().includes(lowerCaseQuery)
  );
});

const openCreateModal = () => {
  selectedUser.value = null;
  isModalOpen.value = true;
};

const openEditModal = (user) => {
  selectedUser.value = user;
  isModalOpen.value = true;
};

const handleUserSaved = () => {
  isModalOpen.value = false;
  fetchUsers(); // Refresh the user list
};

// Function to handle user deletion
const deleteUser = async (userId) => {
  if (confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
    try {
      await axios.delete(`/api/users/${userId}/`);
      toast.success('Usuario eliminado con éxito.');
      fetchUsers(); // Refresh the list after deletion
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error al eliminar el usuario.';
      toast.error(errorMessage);
      console.error('Failed to delete user:', error);
    }
  }
};

</script>

<template>
  <div class="users-container">
    <div class="users-header">
      <h1>Gestión de Usuarios</h1>
      <button @click="openCreateModal" class="create-btn">
        <font-awesome-icon icon="plus" /> Crear Usuario
      </button>
    </div>

    <div class="filters">
      <input type="text" v-model="searchQuery" placeholder="Buscar por nombre de usuario o email..." class="search-input" />
    </div>

    <div v-if="loading" class="loading-spinner">
      <font-awesome-icon icon="spinner" spin size="3x" />
      <p>Cargando usuarios...</p>
    </div>
    <div v-else-if="filteredUsers.length > 0" class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Activo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>
              <span :class="user.is_active ? 'status-active' : 'status-inactive'">
                {{ user.is_active ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="actions">
              <button @click="openEditModal(user)" class="action-btn edit-btn" title="Editar usuario">✏️</button>
              <button @click="deleteUser(user.id)" class="action-btn delete-btn" title="Eliminar usuario">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="no-users">
      <p>No se encontraron usuarios.</p>
    </div>

    <!-- Modal for creating/editing users -->
    <UserFormModal 
      :show="isModalOpen" 
      :user="selectedUser" 
      @close="isModalOpen = false"
      @user-saved="handleUserSaved"
    />
  </div>
</template>

<style scoped>
.users-container { max-width: 1200px; margin: 40px auto; padding: 30px; background: var(--color-neutral); border-radius: 15px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1); }
.users-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.create-btn { background-color: var(--color-primary); color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; }
.filters { margin-bottom: 20px; }
.search-input { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
.loading-spinner, .no-users { text-align: center; padding: 40px; color: var(--color-text-muted); }
.users-table-container { overflow-x: auto; }
.users-table { width: 100%; border-collapse: collapse; }
.users-table th, .users-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
.users-table th { background-color: #f8f9fa; font-weight: 500; }

.status-active { color: #28a745; font-weight: bold; }
.status-inactive { color: #dc3545; font-weight: bold; }

.actions { display: flex; gap: 10px; }
.action-btn { background: none; border: 1px solid #ccc; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
.edit-btn:hover { border-color: #007bff; }
.delete-btn:hover { border-color: #dc3545; }
</style>
