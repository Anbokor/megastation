<script setup>
import { useUserStore } from "@/store/user";
import { storeToRefs } from "pinia";

const userStore = useUserStore();
const { user, loading, error } = storeToRefs(userStore);

// Если данные пользователя еще не загружены, можно инициировать загрузку
if (!user.value) {
  userStore.fetchUser();
}
</script>

<template>
  <div class="profile-container">
    <h1>Perfil de Usuario</h1>
    <div v-if="loading" class="loading-spinner">
      <font-awesome-icon icon="spinner" spin size="3x" />
      <p>Cargando perfil...</p>
    </div>
    <div v-else-if="error" class="error-message">
      <p>Ha ocurrido un error al cargar el perfil: {{ error }}</p>
    </div>
    <div v-else-if="user" class="profile-card">
      <div class="profile-header">
        <font-awesome-icon icon="user" size="2x" />
        <h2>{{ user.username }}</h2>
      </div>
      <div class="profile-details">
        <div class="detail-item">
          <strong>Email:</strong>
          <span>{{ user.email }}</span>
        </div>
        <div class="detail-item">
          <strong>Rol:</strong>
          <span>{{ user.role }}</span>
        </div>
        <div v-if="user.sales_point" class="detail-item">
          <strong>Punto de Venta:</strong>
          <span>{{ user.sales_point_name || 'No asignado' }}</span>
        </div>
      </div>
    </div>
    <div v-else class="not-logged-in">
      <p>Por favor, inicia sesión para ver tu perfil.</p>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 30px;
  background: var(--color-neutral);
  border-radius: 15px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.loading-spinner, .error-message, .not-logged-in {
  padding: 40px;
  color: var(--color-text-muted);
}

.profile-card {
  text-align: left;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.profile-header h2 {
  margin: 0;
  font-size: 1.8em;
  color: var(--color-primary);
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.detail-item strong {
  color: var(--color-secondary);
}
</style>
