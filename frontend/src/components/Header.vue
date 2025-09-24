<script setup>
import { useRouter } from "vue-router";
import { useCartStore } from "@/store/cart";
import { useUserStore } from "@/store/user";
import { ref, onMounted, computed } from "vue";
import { useToast } from "vue-toastification";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
// Import the new icon for users
import { faHome, faList, faShoppingCart, faSignInAlt, faSignOutAlt, faBars, faSearch, faChartPie, faUser, faFileInvoice, faBoxesStacked, faUsers } from "@fortawesome/free-solid-svg-icons";
import { library } from "@fortawesome/fontawesome-svg-core";

// Add the new icon to the library
library.add(faHome, faList, faShoppingCart, faSignInAlt, faSignOutAlt, faBars, faSearch, faChartPie, faUser, faFileInvoice, faBoxesStacked, faUsers);

const router = useRouter();
const cartStore = useCartStore();
const userStore = useUserStore();
const searchQuery = ref("");
const isMobileMenuOpen = ref(false);
const toast = useToast();

// Computed property to determine if the user is staff. This is the correct way.
const isStaff = computed(() => {
  if (!userStore.isAuthenticated || !userStore.getUser) {
    return false;
  }
  const userRole = userStore.getUser.role;
  return ['superuser', 'admin', 'store_admin'].includes(userRole);
});

const searchProducts = () => {
  router.push({ path: "/catalog", query: { search: searchQuery.value } });
};

const logout = () => {
  userStore.logout();
  toast.success("¡Has cerrado sesión correctamente!");
  router.push("/login").catch(() => {
    toast.error("Error al redirigir.");
  });
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

// The erroneous API call has been removed from onMounted
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
        <font-awesome-icon icon="search" class="search-icon" />
        <input v-model="searchQuery" placeholder="Buscar productos..." @keyup.enter="searchProducts" />
      </div>
      <nav :class="{ 'mobile-open': isMobileMenuOpen }">
        <router-link to="/">Inicio</router-link>
        <router-link to="/catalog">Catálogo</router-link>
        <router-link to="/cart">Carrito ({{ cartStore.totalItems }})</router-link>
        
        <template v-if="userStore.isAuthenticated">
          <!-- Staff-specific links -->
          <router-link v-if="isStaff" to="/users">Usuarios</router-link>
          <router-link v-if="isStaff" to="/dashboard">Dashboard</router-link>
          <router-link v-if="isStaff" to="/invoices">Facturas</router-link>
          <router-link v-if="isStaff" to="/stock-levels">Inventario</router-link>
          <router-link v-if="isStaff" to="/staff-orders">Pedidos Staff</router-link>

          <!-- Regular user link -->
          <router-link v-if="!isStaff" to="/orders">Mis Pedidos</router-link>
          
          <router-link to="/profile">Mi Perfil</router-link>
          <button @click="logout" class="logout-btn">Salir</button>
        </template>

        <template v-else>
          <router-link to="/login" class="login-btn">Iniciar Sesión</router-link>
        </template>
      </nav>
      <button class="menu-toggle" @click="toggleMobileMenu"><font-awesome-icon icon="bars" /></button>
    </div>
  </header>
</template>

<style scoped>
.header {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  padding: 0 var(--spacing-5);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  height: 80px;
}

.header-container {
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  height: 50px; /* Adjusted logo size */
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-2) var(--spacing-3);
  width: 320px;
}

.search-icon {
  color: var(--color-text-secondary);
  margin-right: var(--spacing-2);
}

.search-bar input {
  border: none;
  outline: none;
  background: none;
  width: 100%;
  font-family: var(--font-family-base);
  font-size: 1em;
}

nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-5);
}

nav a {
  color: var(--color-text-secondary);
  font-weight: 500;
  padding: var(--spacing-2) 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease, border-color 0.2s ease;
}

nav a:hover {
  color: var(--color-text-primary);
}

nav a.router-link-exact-active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.login-btn, .logout-btn {
  border: none;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-2) var(--spacing-4);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-btn {
  background-color: var(--color-primary);
  color: white;
}

.login-btn:hover {
  background-color: var(--color-primary-hover);
}

.logout-btn {
  background-color: transparent;
  color: var(--color-text-secondary);
}

.logout-btn:hover {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.menu-toggle {
  display: none; /* Hidden on desktop */
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: 24px;
  cursor: pointer;
}

/* Mobile Styles */
@media (max-width: 1024px) {
  .search-bar { display: none; }
  nav { gap: var(--spacing-4); }
}

@media (max-width: 768px) {
  .menu-toggle { display: block; }
  nav {
    display: none;
    position: absolute;
    top: 80px;
    left: 0;
    right: 0;
    background-color: var(--color-surface);
    flex-direction: column;
    padding: var(--spacing-4);
    box-shadow: var(--shadow-lg);
    gap: 0;
  }
  nav.mobile-open { display: flex; }
  nav a, nav button {
    width: 100%;
    padding: var(--spacing-3);
    text-align: center;
    border-bottom: 1px solid var(--color-border);
  }
  nav a:last-of-type, nav button:last-of-type {
    border-bottom: none;
  }
}
</style>
