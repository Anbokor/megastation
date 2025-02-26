<template>
  <div class="login-container">
    <h1>🔑 Iniciar sesión</h1>
    <form @submit.prevent="login">
      <div class="input-group">
        <label for="username">Usuario</label>
        <input v-model="username" type="text" id="username" required />
      </div>
      <div class="input-group">
        <label for="password">Contraseña</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? "🔄 Iniciando sesión..." : "Iniciar sesión" }}
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const router = useRouter();
const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref(null);

const login = async () => {
  error.value = null;
  loading.value = true;
  try {
    await userStore.login(username.value, password.value);
    router.push("/"); // ✅ После входа перенаправляем на главную
  } catch (err) {
    error.value = "Error de autenticación. Verifique su usuario y contraseña.";
  }
  loading.value = false;
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.input-group {
  margin-bottom: 15px;
  text-align: left;
}

.input-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.input-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  width: 100%;
  padding: 10px;
  background: #17BEDB;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background: #10A4C7;
}

button:disabled {
  background: #ccc;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
