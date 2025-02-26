<template>
  <header>
    <div class="logo-container">
      <router-link to="/">
        <img :src="logoSrc" alt="Megastation Logo" class="logo" />
      </router-link>
    </div>

    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="Buscar productos..." @keyup.enter="searchProducts" />
      <button @click="searchProducts">🔍</button>
    </div>

    <nav>
      <ul>
        <li><router-link to="/">Inicio</router-link></li>
        <li><router-link to="/catalog">Catálogo</router-link></li>
        <li><router-link to="/cart">🛒 Carrito ({{ cartStore.totalItems }})</router-link></li>
        <li v-if="!userStore.isAuthenticated"><router-link to="/login">Iniciar Sesión</router-link></li>
        <li v-else><button @click="logout">Salir</button></li>
      </ul>
    </nav>
  </header>
</template>

<script setup>
import { useCartStore } from "@/store/cart";
import { useUserStore } from "@/store/user";
import { ref, computed } from "vue";
import logo from "@/assets/logo.png";

const cartStore = useCartStore();
const userStore = useUserStore();
const logoSrc = logo || "/static/default-logo.png";
const searchQuery = ref("");

const searchProducts = () => {
  console.log("🔍 Buscando:", searchQuery.value);
};

const logout = () => {
  userStore.logout();
};
</script>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #006899;
  padding: 15px 20px;
  color: white;
}

.logo {
  height: 50px;
}

.search-bar {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 20px;
  padding: 5px 10px;
}

.search-bar input {
  border: none;
  outline: none;
  padding: 5px;
  width: 200px;
}

.search-bar button {
  background: none;
  border: none;
  cursor: pointer;
}

nav ul {
  display: flex;
  list-style: none;
}

nav ul li {
  margin: 0 15px;
}

nav ul li a,
nav ul li button {
  color: white;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}
</style>
