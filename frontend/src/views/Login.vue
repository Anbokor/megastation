<script setup>
import { ref } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const router = useRouter();
const isLogin = ref(true); // Переключение между логином и регистрацией
const username = ref("");
const password = ref("");
const email = ref(""); // Для регистрации
const loading = ref(false);
const error = ref(null);

// Функция для входа
const login = async () => {
  error.value = null;
  loading.value = true;
  try {
    await userStore.login({ username: username.value, password: password.value });
    router.push("/");
  } catch (err) {
    error.value = "Error de autenticación. Verifica tus datos.";
  }
  loading.value = false;
};

// Функция для регистрации (только клиенты)
const register = async () => {
  error.value = null;
  loading.value = true;
  try {
    await userStore.register({ username: username.value, password: password.value, email: email.value });
    alert("¡Registro exitoso! Ahora puedes iniciar sesión.");
    isLogin.value = true; // Переключаемся на форму входа
  } catch (err) {
    error.value = "Error al registrar. Verifica los datos o intenta de nuevo.";
  }
  loading.value = false;
};
</script>

<template>
  <div class="login">
    <h1>{{ isLogin ? "🔑 Iniciar Sesión" : "📋 Registrarse" }}</h1>
    <div class="toggle-buttons">
      <button @click="isLogin = true" :class="{ 'active': isLogin }">Iniciar Sesión</button>
      <button @click="isLogin = false" :class="{ 'active': !isLogin }">Registrarse</button>
    </div>
    <form @submit.prevent="isLogin ? login() : register()" class="login-form">
      <div class="input-group">
        <label><font-awesome-icon icon="user" /> Usuario</label>
        <input v-model="username" type="text" required />
      </div>
      <div class="input-group" :class="{ 'hidden': !isLogin }">
        <label><font-awesome-icon icon="lock" /> Contraseña</label>
        <input v-model="password" type="password" required />
      </div>
      <div v-if="!isLogin" class="input-group">
        <label><font-awesome-icon icon="envelope" /> Email</label>
        <input v-model="email" type="email" required />
      </div>
      <div v-if="!isLogin" class="input-group">
        <label><font-awesome-icon icon="lock" /> Contraseña</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="loading">
        <font-awesome-icon :icon="isLogin ? 'sign-in-alt' : 'user-plus'" /> {{ loading ? "🔄 Procesando..." : isLogin ? "Iniciar Sesión" : "Registrarse" }}
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
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
  transition: background 0.3s ease, transform 0.3s ease;
}

.toggle-buttons button.active {
  background: var(--color-primary);
}

.toggle-buttons button:hover:not(.active) {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group.hidden {
  display: none;
}

.input-group label {
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  border-color: var(--color-primary);
  outline: none;
}

button {
  width: 100%;
  background: var(--color-accent);
  color: var(--color-neutral);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

button:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

button:disabled {
  background: gray;
}

.error {
  color: #D9534F;
  margin-top: 15px;
  text-align: center;
}

@media (max-width: 768px) {
  .login {
    margin: 40px auto 10px;
    padding: 20px;
  }

  .login-form {
    gap: 15px;
  }

  .toggle-buttons {
    flex-direction: column;
  }

  .toggle-buttons button {
    padding: 8px;
  }
}
</style>