<script setup>
import { ref } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

const userStore = useUserStore();
const router = useRouter();
const toast = useToast();
const isLogin = ref(true);
const username = ref("");
const password = ref("");
const email = ref("");
const loading = ref(false);
const errors = ref({});

const validateForm = () => {
  errors.value = {};
  if (!username.value) errors.value.username = "Usuario es obligatorio";
  if (!password.value) errors.value.password = "Contraseña es obligatoria";
  if (!isLogin.value && !email.value) errors.value.email = "Email es obligatorio";
  if (!isLogin.value && email.value && !/\S+@\S+\.\S+/.test(email.value)) {
    errors.value.email = "Introduce un correo válido";
  }
  return Object.keys(errors.value).length === 0;
};

const submitAction = async () => {
  if (!validateForm()) {
    toast.warning("Por favor, corrige los errores del formulario.");
    return;
  }
  loading.value = true;
  try {
    if (isLogin.value) {
      await userStore.login({ username: username.value, password: password.value });
      toast.success("¡Inicio de sesión exitoso!");
    } else {
      await userStore.register({ username: username.value, password: password.value, email: email.value });
      toast.success("¡Registro exitoso! Serás redirigido.");
    }
    router.push("/");
  } catch (err) {
    toast.error(err.message || "Ocurrió un error inesperado.");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card card">
      <div class="toggle-buttons">
        <button @click="isLogin = true" :class="{ active: isLogin }">Iniciar Sesión</button>
        <button @click="isLogin = false" :class="{ active: !isLogin }">Registrarse</button>
      </div>

      <form @submit.prevent="submitAction" class="login-form">
        <h2>{{ isLogin ? "Bienvenido de Nuevo" : "Crear una Cuenta" }}</h2>
        
        <div class="input-group">
          <label for="username">Usuario</label>
          <input id="username" v-model="username" type="text" :class="{ 'error': errors.username }" placeholder="tu-usuario" />
          <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
        </div>

        <div class="input-group">
          <label for="password">Contraseña</label>
          <input id="password" v-model="password" type="password" :class="{ 'error': errors.password }" placeholder="••••••••" />
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </div>

        <div v-if="!isLogin" class="input-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" :class="{ 'error': errors.email }" placeholder="tu@email.com" />
          <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </div>

        <button type="submit" :disabled="loading" class="btn btn-primary submit-btn">
          {{ loading ? "Procesando..." : (isLogin ? "Iniciar Sesión" : "Crear Cuenta") }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* Adjust for header height */
  padding: var(--spacing-5);
}

.login-card {
  width: 100%;
  max-width: 420px;
}

.toggle-buttons {
  display: flex;
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-1);
  margin-bottom: var(--spacing-6);
}

.toggle-buttons button {
  flex: 1;
  padding: var(--spacing-3);
  border: none;
  border-radius: var(--border-radius-sm);
  background-color: transparent;
  color: var(--color-text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-buttons button.active {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
}

.login-form h2 {
  text-align: center;
  margin-bottom: var(--spacing-5);
}

.input-group {
  margin-bottom: var(--spacing-4);
}

.input-group label {
  display: block;
  font-weight: 500;
  margin-bottom: var(--spacing-2);
}

.input-group input {
  width: 100%;
  padding: var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background-color: var(--color-background);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.input-group input.error {
  border-color: #ef4444;
}

.error-text {
  color: #ef4444;
  font-size: 0.875em;
  margin-top: var(--spacing-1);
}

.submit-btn {
  width: 100%;
  margin-top: var(--spacing-5);
}
</style>
