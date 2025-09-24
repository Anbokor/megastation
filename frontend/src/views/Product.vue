<script setup>
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";
import { useToast } from "vue-toastification";

const route = useRoute();
const productStore = useProductStore();
const cartStore = useCartStore();
const toast = useToast();

const defaultImage = "/media/default_product.jpg";

onMounted(() => productStore.fetchProduct(route.params.id));
watch(() => route.params.id, newId => productStore.fetchProduct(newId));

const product = computed(() => productStore.currentProduct);

const addToCart = () => {
  if (product.value && product.value.availability === "available") {
    cartStore.addToCart(product.value);
    toast.success("Producto añadido al carrito.");
  } else {
    toast.warning("Producto bajo pedido.");
  }
};
</script>

<template>
  <div class="product">
    <div v-if="productStore.loading" class="loading">
      <font-awesome-icon icon="spinner" spin /> Cargando producto...
    </div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
    <div v-else-if="product" class="product-detail">
      <img :src="product.image || defaultImage" :alt="product.name" />
      <div class="info">
        <h1>{{ product.name }}</h1>
        <p class="description">{{ product.description }}</p>
        <p class="price">ARS {{ product.price }}</p>
        <p :class="{ 'out-of-stock': product.availability === 'on_order' }">
          📦 {{ product.availability === "available" ? "Disponible" : "Bajo pedido" }}
        </p>
        <button
          :disabled="product.availability === 'on_order'"
          @click="addToCart"
          class="add-btn"
          :title="product.availability === 'available' ? 'Añadir al carrito' : 'Producto no disponible'"
        >
          <font-awesome-icon icon="shopping-cart" />
          {{ product.availability === "available" ? "Agregar al carrito" : "Bajo pedido" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product { max-width: 900px; margin: 60px auto 20px; padding: 40px; background: var(--color-surface); border-radius: 20px; box-shadow: var(--shadow-lg); }
.product-detail { display: flex; gap: 40px; }
img { max-width: 400px; height: auto; border-radius: 15px; object-fit: contain; }
.info { flex: 1; padding: 20px 0; }
.description { color: var(--color-text-secondary); font-size: 1.1em; line-height: 1.6; margin: 10px 0; }
.price { font-size: 2.5em; color: var(--color-primary); font-weight: 700; margin: 20px 0; }
.out-of-stock { color: var(--color-text-secondary); font-weight: 500; }
.add-btn { background-color: var(--color-primary); color: white; padding: 15px 30px; border: none; border-radius: var(--border-radius-md); cursor: pointer; transition: background-color 0.2s ease; font-size: 1.1em; }
.add-btn:hover:not(:disabled) { background-color: var(--color-primary-hover); }
.add-btn:disabled { background-color: #ccc; cursor: not-allowed; }
.loading, .error { text-align: center; padding: 20px; }
</style>
