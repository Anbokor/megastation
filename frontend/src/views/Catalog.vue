<script setup>
import { ref, computed, onMounted } from "vue";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";
import { useRoute } from "vue-router";

const productStore = useProductStore();
const cartStore = useCartStore();
const route = useRoute();
const selectedCategory = ref("");
const searchQuery = ref("");

const filteredProducts = computed(() => {
  let products = productStore.products;
  if (selectedCategory.value) {
    products = products.filter(p => p.category_id === parseInt(selectedCategory.value));
  }
  if (searchQuery.value) {
    products = products.filter(p =>
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  return products;
});

onMounted(() => {
  if (!productStore.products.length) productStore.fetchProducts();
  if (!productStore.categories.length) productStore.fetchCategories();
  searchQuery.value = route.query.search || "";
});
</script>

<template>
  <div class="catalog">
    <h1>📦 Catálogo de Productos</h1>
    <div class="filters">
      <input v-model="searchQuery" placeholder="Buscar..." />
      <select v-model="selectedCategory">
        <option value="">Todas las categorías</option>
        <option v-for="cat in productStore.categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
    </div>
    <div v-if="productStore.loading" class="loading">🔄 Cargando...</div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
    <div v-else-if="productStore.products.length === 0" class="empty">No hay productos disponibles.</div>
    <div v-else class="product-grid">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <router-link :to="'/product/' + product.id">
          <img :src="product.image_url || '/static/default-product.jpg'" :alt="product.name" />
          <h2>{{ product.name }}</h2>
          <p>$ {{ product.price }}</p>
        </router-link>
        <button @click="cartStore.addToCart(product)">
          <font-awesome-icon icon="shopping-cart" /> Agregar
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Стили остаются без изменений */
.catalog {
  padding: 20px;
  background: linear-gradient(to bottom, rgba(23, 190, 219, 0.2), var(--color-neutral));
  position: relative;
  overflow: hidden;
}

.catalog::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(16, 164, 199, 0.1), transparent);
  opacity: 0.4;
  z-index: 0;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  background: var(--color-neutral);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

input, select {
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease;
}

input:focus, select:focus {
  border-color: var(--color-primary);
  outline: none;
}

input {
  flex-grow: 1;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 30px;
  margin-top: 20px;
  z-index: 1;
}

.product-card {
  background: var(--color-neutral);
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.product-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(23, 190, 219, 0.2), transparent);
  opacity: 0.3;
  z-index: 0;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.product-card img {
  max-width: 100%;
  border-radius: 10px;
  background: #f8f8f8;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card img:hover {
  transform: scale(1.05);
}

.product-card a {
  text-decoration: none;
  color: var(--color-text);
  z-index: 1;
  position: relative;
}

button {
  background: var(--color-primary);
  color: var(--color-neutral);
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
  z-index: 1;
  position: relative;
}

button:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.loading, .error, .empty {
  text-align: center;
  padding: 20px;
  z-index: 1;
}

.error {
  color: #D9534F;
}

@media (max-width: 768px) {
  .catalog {
    padding: 15px;
  }

  .filters {
    flex-direction: column;
    gap: 10px;
  }

  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
  }
}
</style>