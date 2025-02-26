<template>
  <div class="container">
    <h1>📦 Catálogo de Productos</h1>

    <div class="filters">
      <label>
        Categoría:
        <select v-model="selectedCategory" @change="filterProducts">
          <option value="">Todas</option>
          <option v-for="category in productStore.categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </label>
    </div>

    <div v-if="productStore.loading">🔄 Cargando productos...</div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>

    <div v-else class="product-list">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <router-link :to="'/product/' + product.id">
          <img :src="product.image_url" :alt="product.name" class="product-image" />
          <h2>{{ product.name }}</h2>
          <p>💲{{ product.price }}</p>
        </router-link>
        <button @click="cartStore.addToCart(product)">🛒 Agregar al carrito</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, ref, onMounted} from "vue";
import {useProductStore} from "@/store/products";
import {useCartStore} from "@/store/cart";

const productStore = useProductStore();
const cartStore = useCartStore();
const selectedCategory = ref("");

const filteredProducts = computed(() => {
  return selectedCategory.value
      ? productStore.products.filter(product => product.category_id === selectedCategory.value)
      : productStore.products;
});

const filterProducts = () => {
  console.log("Filtrando por categoría:", selectedCategory.value);
};

onMounted(() => {
  productStore.fetchProducts();
  productStore.fetchCategories();
});
</script>
