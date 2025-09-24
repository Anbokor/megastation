<script setup>
import { ref, computed, onMounted } from "vue";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

const productStore = useProductStore();
const cartStore = useCartStore();
const route = useRoute();
const toast = useToast();
const selectedCategory = ref("");
const searchQuery = ref("");
const sortOption = ref("price_asc");

const filteredProducts = computed(() => {
  let products = [...productStore.products];
  if (selectedCategory.value) {
    products = products.filter(p => p.category_id === parseInt(selectedCategory.value));
  }
  if (searchQuery.value) {
    products = products.filter(p =>
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  switch (sortOption.value) {
    case "price_asc":
      products.sort((a, b) => {
        const priceA = Number(a.price) || 0;
        const priceB = Number(b.price) || 0;
        return priceA - priceB;
      });
      break;
    case "price_desc":
      products.sort((a, b) => {
        const priceA = Number(a.price) || 0;
        const priceB = Number(b.price) || 0;
        return priceB - priceA;
      });
      break;
    case "name_asc":
      products.sort((a, b) => a.name.localeCompare(b.name));
      break;
  }
  return products;
});

onMounted(async () => {
  try {
    if (!productStore.products.length) await productStore.fetchProducts();
    if (!productStore.categories.length) await productStore.fetchCategories();
    searchQuery.value = route.query.search || "";
  } catch (error) {
    toast.error("Error al cargar el catálogo.");
  }
});

const addToCart = (product) => {
  if (product.availability === "available") {
    // FIX: The notification logic is now handled entirely by the cart store
    // to provide accurate feedback (added vs. quantity increased).
    cartStore.addToCart(product);
  } else {
    toast.warning("Este producto solo está disponible bajo pedido.");
  }
};
</script>

<template>
  <div class="catalog">
    <h1>Catálogo de Productos</h1>
    <div class="filters">
      <input v-model="searchQuery" placeholder="Buscar productos..." />
      <select v-model="selectedCategory">
        <option value="">Todas las categorías</option>
        <option v-for="cat in productStore.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
      <select v-model="sortOption">
        <option value="price_asc">Precio: Menor a Mayor</option>
        <option value="price_desc">Precio: Mayor a Menor</option>
        <option value="name_asc">Nombre (A-Z)</option>
      </select>
    </div>
    <div v-if="productStore.loading" class="loading">Cargando...</div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
    <div v-else-if="filteredProducts.length === 0" class="empty">No se encontraron productos.</div>
    <div v-else class="product-grid">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <router-link :to="'/product/' + product.id" class="product-main-link">
          <div class="image-container">
            <img :src="product.image || '/media/default_product.jpg'" :alt="product.name" />
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="price">ARS {{ product.price }}</p>
          </div>
        </router-link>
        <div class="product-actions">
            <p :class="['availability', product.availability === 'on_order' ? 'on-order' : '']">
              {{ product.availability === "available" ? "Disponible" : "Bajo pedido" }}
            </p>
            <button @click="addToCart(product)" class="add-btn">
              <font-awesome-icon icon="shopping-cart" /> Agregar
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog { padding: var(--spacing-5); }
.filters { display: flex; flex-wrap: wrap; gap: var(--spacing-4); margin-bottom: var(--spacing-5); }
.filters input, .filters select { padding: var(--spacing-2) var(--spacing-3); border: 1px solid var(--color-border); border-radius: var(--border-radius-md); font-size: 1em; }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--spacing-5); }

.product-card {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Ensures content respects border radius */
}

.product-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-lg); }

.product-main-link { text-decoration: none; color: inherit; display: flex; flex-direction: column; flex-grow: 1; }

.image-container {
  width: 100%;
  height: 220px; /* Fixed height for the image area */
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-card img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain; /* This ensures the whole image is visible */
}

.product-info {
  padding: var(--spacing-4);
  text-align: center;
  flex-grow: 1;
}

.product-info h3 { font-size: 1.1em; margin: 0 0 var(--spacing-2) 0; }
.price { font-size: 1.2em; font-weight: 600; color: var(--color-primary); margin: 0; }

.product-actions {
  padding: 0 var(--spacing-4) var(--spacing-4);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.availability { margin: 0 0 var(--spacing-3); font-weight: 500; }
.on-order { color: var(--color-text-secondary); }

.add-btn {
  width: 100%;
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-3);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.add-btn:hover { background-color: var(--color-primary-hover); }

.loading, .error, .empty { text-align: center; padding: 50px; font-size: 1.2em; }
</style>
