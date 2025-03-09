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

const submitAction = async (actionType) => {
  if (!validateForm()) {
    toast.warning("Por favor, corrige los errores en el formulario.", {
      toastClassName: "custom-toast-warning",
    });
    return;
  }
  loading.value = true;
  try {
    if (actionType === "login") {
      await userStore.login({ username: username.value, password: password.value });
      toast.success("¡Inicio de sesión exitoso!", {
        icon: "✅",
        toastClassName: "custom-toast-success",
      });
    } else {
      await userStore.register({ username: username.value, password: password.value, email: email.value });
      toast.success("¡Registro exitoso!", {
        icon: "✅",
        toastClassName: "custom-toast-success",
      });
    }
    router.push("/").catch((err) => {
      toast.error(`Error al redirigir: ${err.message}`, {
        toastClassName: "custom-toast-error",
      });
    });
  } catch (err) {
    toast.error(err.message || "Ocurrió un error inesperado.", {
      icon: "❌",
      toastClassName: "custom-toast-error",
    });
  } finally {
    loading.value = false;
  }
};

const login = () => submitAction("login");
const register = () => submitAction("register");
</script>

<template>
  <div class="login">
    <h1>{{ isLogin ? "🔑 Iniciar Sesión" : "📋 Registrarse" }}</h1>
    <div class="toggle-buttons">
      <button
        @click="isLogin = true"
        :class="{ 'active': isLogin }"
        title="Accede con tu cuenta existente"
      >
        Iniciar Sesión
      </button>
      <button
        @click="isLogin = false"
        :class="{ 'active': !isLogin }"
        title="Crea una nueva cuenta"
      >
        Registrarse
      </button>
    </div>
    <form @submit.prevent="isLogin ? login() : register()" class="login-form">
      <div class="input-group">
        <label title="Introduce tu nombre de usuario (mínimo 3 caracteres)">
          <font-awesome-icon icon="user" /> Usuario
        </label>
        <input
          v-model="username"
          type="text"
          :class="{ 'error': errors.username }"
          autocomplete="username"
          placeholder="Ej: juan123"
          @input="errors.username = null"
        />
        <transition name="fade">
          <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
        </transition>
      </div>
      <div class="input-group">
        <label title="Introduce tu contraseña (mínimo 6 caracteres)">
          <font-awesome-icon icon="lock" /> Contraseña
        </label>
        <input
          v-model="password"
          type="password"
          :class="{ 'error': errors.password }"
          autocomplete="current-password"
          placeholder="••••••"
          @input="errors.password = null"
        />
        <transition name="fade">
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </transition>
      </div>
      <div v-if="!isLogin" class="input-group">
        <label title="Introduce tu correo electrónico (ejemplo@dominio.com)">
          <font-awesome-icon icon="envelope" /> Email
        </label>
        <input
          v-model="email"
          type="email"
          :class="{ 'error': errors.email }"
          autocomplete="email"
          placeholder="Ej: juan@ejemplo.com"
          @input="errors.email = null"
        />
        <transition name="fade">
          <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </transition>
      </div>
      <button
        type="submit"
        :disabled="loading"
        class="submit-btn"
        :class="{ 'loading': loading }"
        :title="loading ? 'Procesando tu solicitud...' : isLogin ? 'Inicia sesión ahora' : 'Regístrate ahora'"
      >
        <font-awesome-icon v-if="loading" icon="spinner" spin />
        <font-awesome-icon v-else :icon="isLogin ? 'sign-in-alt' : 'user-plus'" />
        {{ loading ? "Procesando..." : isLogin ? "Iniciar Sesión" : "Registrarse" }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login {
  max-width: 450px;
  margin: 60px auto 20px;
  padding: 40px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.login:hover {
  transform: translateY(-2px);
}

.login::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(23, 190, 219, 0.1), transparent);
  opacity: 0.3;
  z-index: 0;
}

.login-form {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toggle-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.toggle-buttons button {
  flex: 1;
  padding: 10px;
  background: var(--color-secondary);
  color: var(--color-neutral);
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: background 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
}

.toggle-buttons button.active {
  background: var(--color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.toggle-buttons button:hover:not(.active) {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group label {
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  cursor: help;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  background: #f9f9f9;
}

.input-group input:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 8px rgba(16, 164, 199, 0.3);
}

.input-group input.error {
  border-color: #D9534F;
  box-shadow: 0 0 8px rgba(217, 83, 79, 0.3);
}

.input-group input::placeholder {
  color: #999;
  opacity: 0.8;
}

.error-text {
  color: #D9534F;
  font-size: 0.9rem;
  margin-top: 5px;
}

.submit-btn {
  width: 100%;
  background: var(--color-accent);
  color: var(--color-neutral);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.submit-btn:disabled {
  background: #b0b0b0;
  cursor: not-allowed;
  box-shadow: none;
}

.submit-btn.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: ripple 1.5s infinite;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes ripple {
  0% {
    width: 0;
    height: 0;
  }
  50% {
    width: 120px;
    height: 120px;
  }
  100% {
    width: 0;
    height: 0;
  }
}

/* Кастомизация тостов */
:deep(.custom-toast-success) {
  background-color: var(--color-primary);
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-error) {
  background-color: #D9534F;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-warning) {
  background-color: #F0AD4E;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}
</style>