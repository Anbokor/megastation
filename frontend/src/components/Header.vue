<script setup>
import { useRouter } from "vue-router";
import { useCartStore } from "@/store/cart";
import { useUserStore } from "@/store/user";
import { ref, onMounted } from "vue";
import { useToast } from "vue-toastification";

const router = useRouter();
const cartStore = useCartStore();
const userStore = useUserStore();
const searchQuery = ref("");
const isMobileMenuOpen = ref(false);
const toast = useToast();

const searchProducts = () => {
  router.push({ path: "/catalog", query: { search: searchQuery.value } });
};

const logout = () => {
  userStore.logout();
  toast.success("¡Has cerrado sesión correctamente!", {
    toastClassName: "custom-toast-success",
  });
  router.push("/login").catch(() => {
    toast.error("Error al redirigir.", {
      toastClassName: "custom-toast-error",
    });
  });
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

onMounted(async () => {
  if (userStore.isAuthenticated && !userStore.getUser) {
    await userStore.fetchUser();
  }
});
</script>

<template>
  <header class="header">
    <div class="header-container">
      <div class="logo-container">
        <router-link to="/">
          <img src="@/assets/MGST-Logo-Blanco.png" alt="Megastation" class="logo" />
        </router-link>
      </div>
      <div class="search-bar">
        <input v-model="searchQuery" placeholder="Buscar productos..." @keyup.enter="searchProducts" />
        <button @click="searchProducts"><font-awesome-icon icon="search" /></button>
      </div>
      <nav :class="{ 'mobile-open': isMobileMenuOpen }">
        <router-link to="/"><font-awesome-icon icon="home" /> Inicio</router-link>
        <router-link to="/catalog"><font-awesome-icon icon="list" /> Catálogo</router-link>
        <router-link to="/cart"><font-awesome-icon icon="shopping-cart" /> Carrito ({{ cartStore.totalItems }})</router-link>
        <router-link v-if="userStore.isAuthenticated && ['superuser', 'admin', 'store_admin'].includes(userStore.getUser?.role)" to="/dashboard">
          <font-awesome-icon :icon="['fas', 'chart-pie']" /> Dashboard
        </router-link>
        <router-link v-if="!userStore.isAuthenticated" to="/login"><font-awesome-icon icon="sign-in-alt" /> Iniciar Sesión</router-link>
        <button v-else @click="logout"><font-awesome-icon icon="sign-out-alt" /> Salir</button>
      </nav>
      <button class="menu-toggle" @click="toggleMobileMenu"><font-awesome-icon icon="bars" /></button>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: linear-gradient(to right, var(--color-secondary), var(--color-primary));
  padding: 10px 20px;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.logo-container {
  padding: 10px;
}

.logo {
  height: 80px;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.search-bar {
  display: flex;
  background: var(--color-neutral);
  border-radius: 25px;
  padding: 5px;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
}

.search-bar input {
  border: none;
  outline: none;
  padding: 8px;
  width: 280px;
  border-radius: 25px 0 0 25px;
  font-family: 'Candara', sans-serif;
}

.search-bar button {
  background: var(--color-accent);
  border: none;
  padding: 8px 12px;
  border-radius: 0 25px 25px 0;
  cursor: pointer;
  color: var(--color-neutral);
  transition: background 0.3s ease;
}

.search-bar button:hover {
  background: var(--color-accent-hover);
}

nav {
  display: flex;
  align-items: center;
}

nav a,
nav button {
  color: var(--color-neutral);
  margin: 0 10px;
  text-decoration: none;
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  transition: color 0.3s ease;
}

nav a svg,
nav button svg {
  margin-right: 5px;
}

nav button {
  background: none;
  border: none;
  cursor: pointer;
}

nav a:hover,
nav button:hover {
  color: var(--color-neutral-light);
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--color-neutral);
  font-size: 24px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: row;
    justify-content: space-between;
  }

  .logo {
    height: 60px;
  }

  .search-bar input {
    width: 140px;
    padding: 6px;
  }

  .search-bar button {
    padding: 6px 10px;
  }

  .menu-toggle {
    display: block;
  }

  nav {
    display: none;
    width: 100%;
    flex-direction: column;
    background: var(--color-secondary);
    position: absolute;
    top: 60px;
    left: 0;
    padding: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  }

  nav.mobile-open {
    display: flex;
  }

  nav a,
  nav button {
    margin: 8px 0;
    width: 100%;
    text-align: center;
  }
}

:root {
  --color-neutral-light: #f0f0f0;
}
</style>