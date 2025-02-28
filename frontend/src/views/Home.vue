<script setup>
import { useRouter } from "vue-router";
import { useProductStore } from "@/store/products";
import { onMounted } from "vue";

const router = useRouter();
const productStore = useProductStore();

onMounted(() => productStore.fetchProducts());
</script>

<template>
  <div class="home">
    <div class="banner">
      <img src="@/assets/home-banner.jpg" alt="Banner Megastation" class="banner-image" />
      <div class="banner-content">
        <h1>Bienvenido a Megastation</h1>
        <p>Explora nuestra selección de productos electrónicos.</p>
        <button @click="router.push('/catalog')">Ver Catálogo</button>
      </div>
    </div>
    <div class="content-wrapper">
      <h2>Productos Populares</h2>
      <div class="popular-products">
        <div v-for="product in productStore.products.slice(0, 3)" :key="product.id" class="product-card">
          <router-link :to="'/product/' + product.id">
            <img :src="product.image_url || '/static/default-product.jpg'" :alt="product.name" />
            <h3>{{ product.name }}</h3>
            <p>$ {{ product.price }}</p>
          </router-link>
        </div>
      </div>
    </div>
    <img src="@/assets/water-decor.png" alt="Water Decor" class="water-decor" />
  </div>
</template>

<style scoped>
.home {
  padding: 0;
  background: linear-gradient(to bottom, rgba(16, 164, 199, 0.5), rgba(0, 104, 153, 0.3)), url('@/assets/wave-bg.png') no-repeat center/cover;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(23, 190, 219, 0.3), transparent);
  opacity: 0.6;
  z-index: 0;
}

.banner {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
  border-radius: 0 0 15px 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.banner-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--color-neutral);
  z-index: 2;
  background: rgba(0, 104, 153, 0.8);
  padding: 20px 40px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

button {
  background: var(--color-secondary);
  color: var(--color-neutral);
  border: none;
  padding: 15px 30px;
  font-family: 'Gotham', sans-serif;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

button:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.content-wrapper {
  padding: 60px 20px 20px;
  max-width: 1200px;
  margin: 20px auto;
  background: rgba(255, 255, 255, 0.9); /* Полупрозрачный белый фон */
  border-radius: 15px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 2;
}

.popular-products {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 50px;
}

.product-card {
  background: var(--color-neutral);
  border-radius: 15px;
  padding: 25px;
  width: 240px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.product-card img {
  max-width: 100%;
  border-radius: 10px;
  object-fit: contain;
  background: #f8f8f8;
}

.product-card a {
  text-decoration: none;
  color: var(--color-text);
}

.water-decor {
  position: absolute;
  bottom: -50px;
  left: 0;
  width: 100%;
  opacity: 0.6; /* Увеличил видимость */
  z-index: 1;
}

@media (max-width: 768px) {
  .banner {
    height: 300px;
  }

  .banner-content {
    padding: 15px 20px;
  }

  .content-wrapper {
    padding: 40px 10px 20px;
  }

  .popular-products {
    flex-direction: column;
    align-items: center;
  }

  .product-card {
    width: 100%;
    max-width: 300px;
  }
}
</style>