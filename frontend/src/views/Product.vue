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
    toast.success("Producto añadido al carrito.", {
      toastClassName: "custom-toast-success",
    });
  } else {
    toast.warning("Producto bajo pedido.", {
      toastClassName: "custom-toast-warning",
    });
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
      <img :src="product.image_url || defaultImage" :alt="product.name" />
      <div class="info">
        <h1>{{ product.name }}</h1>
        <p class="description">{{ product.description }}</p>
        <p class="price">$ {{ product.price }}</p>
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
.product {
  max-width: 900px;
  margin: 60px auto 20px;
  padding: 40px;
  background: var(--color-neutral);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.product:hover {
  transform: translateY(-2px);
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
  height: auto;
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
  margin: 10px 0;
}

.price {
  font-size: 32px;
  color: var(--color-primary);
  font-weight: bold;
  margin: 10px 0;
}

.out-of-stock {
  color: #D9534F;
  font-weight: 500;
}

.add-btn {
  background: var(--color-accent);
  color: var(--color-neutral);
  padding: 12px 25px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Gotham', sans-serif;
  font-weight: 500;
  margin-top: 10px;
}

.add-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.add-btn:disabled {
  background: #b0b0b0;
  cursor: not-allowed;
  box-shadow: none;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  z-index: 1;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.error {
  color: #D9534F;
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

/* Custom toast styles */
:deep(.custom-toast-success) {
  background-color: var(--color-primary);
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-error) {
  background-color: #D9534F;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}

:deep(.custom-toast-warning) {
  background-color: #F0AD4E;
  color: var(--color-neutral);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-family: 'Candara', sans-serif;
}
</style>