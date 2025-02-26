<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";

const route = useRoute();
const productStore = useProductStore();
const cartStore = useCartStore();

const product = ref(null);

onMounted(async () => {
  const productId = route.params.id;
  await productStore.fetchProduct(productId);
  product.value = productStore.currentProduct;
});
</script>

<template>
  <div v-if="product" class="product-page">
    <img :src="product.image_url" :alt="product.name" class="product-image" />
    <h1>{{ product.name }}</h1>
    <p class="description">{{ product.description }}</p>
    <p class="price">💲 {{ product.price }}</p>
    <p class="stock">📦 Stock: {{ product.stock }}</p>

    <button @click="cartStore.addToCart(product)">🛒 Agregar al carrito</button>
  </div>

  <div v-else class="loading">🔄 Cargando producto...</div>
</template>

<style scoped>
.product-page {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.product-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: contain;
  background-color: #f8f8f8;
  border-radius: 10px;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #006899;
}

.stock {
  font-size: 18px;
  color: #17BEDB;
}

.description {
  font-size: 16px;
  color: #333;
}

button {
  background-color: #17BEDB;
  color: white;
  border: none;
  padding: 10px;
  margin-top: 10px;
  cursor: pointer;
}

button:hover {
  background-color: #10A4C7;
}
</style>
