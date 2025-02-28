<script setup>
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";

const route = useRoute();
const productStore = useProductStore();
const cartStore = useCartStore();

const defaultImage = "/static/default-product.jpg";

onMounted(() => productStore.fetchProduct(route.params.id));
watch(() => route.params.id, newId => productStore.fetchProduct(newId));

const product = computed(() => productStore.currentProduct);
</script>

<template>
  <div class="product">
    <div v-if="productStore.loading" class="loading">🔄 Cargando...</div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
    <div v-else-if="product" class="product-detail">
      <img :src="product.image_url || defaultImage" :alt="product.name" />
      <div class="info">
        <h1>{{ product.name }}</h1>
        <p class="description">{{ product.description }}</p>
        <p class="price">$ {{ product.price }}</p>
        <p :class="{ 'out-of-stock': product.stock === 0 }">
          📦 {{ product.stock > 0 ? `En stock: ${product.stock}` : "Sin stock" }}
        </p>
        <button v-if="product.stock > 0" @click="cartStore.addToCart(product)">
          <font-awesome-icon icon="shopping-cart" /> 🛒 Agregar al carrito
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Стили остаются без изменений */
.product {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 40px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.product::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(23, 190, 219, 0.1), transparent);
  opacity: 0.4;
  z-index: 0;
}

.product-detail {
  display: flex;
  gap: 40px;
  position: relative;
  z-index: 1;
}

img {
  max-width: 500px;
  border-radius: 15px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  object-fit: contain;
  transition: transform 0.3s ease;
}

img:hover {
  transform: scale(1.05);
}

.info {
  flex: 1;
  padding: 20px 0;
}

.description {
  font-family: 'Candara', sans-serif;
  color: #555;
  font-size: 1.2rem;
  line-height: 1.6;
}

.price {
  font-size: 32px;
  color: var(--color-primary);
  font-weight: bold;
  margin: 15px 0;
}

.out-of-stock {
  color: #D9534F;
  font-weight: 500;
}

button {
  background: var(--color-accent);
  color: var(--color-neutral);
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

button:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .product {
    margin: 40px auto 10px;
    padding: 20px;
  }

  .product-detail {
    flex-direction: column;
    align-items: center;
  }

  img {
    max-width: 100%;
    margin-bottom: 20px;
  }

  .info {
    padding: 0;
  }
}
</style>