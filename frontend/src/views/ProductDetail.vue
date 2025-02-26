<template>
  <div class="product-detail-container">
    <div v-if="productStore.loading">🔄 Cargando producto...</div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>

    <div v-else class="product-detail" v-if="product">
      <img :src="product.image_url || '/static/default-product.jpg'" :alt="product.name" class="product-image" />
      <div class="product-info">
        <h1>{{ product.name }}</h1>
        <p class="description">{{ product.description }}</p>
        <p class="price">💲{{ product.price }}</p>
        <p class="stock" v-if="product.stock > 0">✅ En stock: {{ product.stock }} disponibles</p>
        <p class="stock out-of-stock" v-else>❌ Agotado</p>
        <button v-if="product.stock > 0" @click="cartStore.addToCart(product)">🛒 Agregar al carrito</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";

const route = useRoute();
const productStore = useProductStore();
const cartStore = useCartStore();

onMounted(() => {
  productStore.fetchProduct(route.params.id);
});

const product = computed(() => productStore.selectedProduct);
</script>
