<script setup>
import { useRouter } from "vue-router";
import { useProductStore } from "@/store/products";
import { onMounted } from "vue";
import { useToast } from "vue-toastification";

const router = useRouter();
const productStore = useProductStore();
const toast = useToast();

onMounted(async () => {
  try {
    await productStore.fetchProducts();
  } catch (error) {
    toast.error("Error al cargar productos populares.", {
      toastClassName: "custom-toast-error",
    });
  }
});

const goToCatalog = () => {
  router.push("/catalog").catch(() => {
    toast.error("Error al ir al catálogo.", {
      toastClassName: "custom-toast-error",
    });
  });
};
</script>

<template>
  <div class="home">
    <div class="hero-section">
      <img src="@/assets/home-banner.jpg" alt="Banner Megastation" class="hero-image" />
      <div class="hero-content">
        <h1 class="hero-title">Bienvenido a Megastation</h1>
        <p class="hero-subtitle">Descubre lo último en tecnología</p>
        <button @click="goToCatalog" class="hero-button" title="Explorar catálogo">
          Ver Catálogo
        </button>
      </div>
    </div>
    <div class="content-wrapper">
      <h2 class="section-title">Productos Populares</h2>
      <div v-if="productStore.loading" class="loading">
        <font-awesome-icon icon="spinner" spin /> Cargando...
      </div>
      <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
      <div v-else class="product-grid">
        <div v-for="product in productStore.products.slice(0, 4)" :key="product.id" class="product-card">
          <router-link :to="'/product/' + product.id" class="product-link" :title="'Ver detalles de ' + product.name">
            <div class="product-image-container">
              <img :src="product.image_url || '/static/default-product.jpg'" :alt="product.name" />
            </div>
            <div class="product-info">
              <h3>{{ product.name }}</h3>
              <p>$ {{ product.price }}</p>
            </div>
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
  background: linear-gradient(to bottom, rgba(16, 164, 199, 0.15), rgba(0, 104, 153, 0.05)),
    url('@/assets/wave-bg.png') no-repeat center/cover;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  color: var(--color-text);
  font-family: 'Candara', sans-serif;
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at top, rgba(23, 190, 219, 0.1), transparent 70%);
  opacity: 0.3;
  z-index: 0;
}

.hero-section {
  position: relative;
  height: 500px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.hero-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.85);
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  max-width: 800px;
}

.hero-title {
  font-family: 'Gotham', sans-serif;
  font-size: 3.5rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 20px;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.6rem;
  color: var(--color-secondary);
  margin-bottom: 30px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

.hero-button {
  background: var(--color-primary);
  color: var(--color-neutral);
  border: none;
  padding: 15px 45px;
  font-family: 'Gotham', sans-serif;
  font-size: 1.2rem;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

.hero-button:hover {
  background: var(--color-accent-hover);
  transform: translateY(-4px);
}

.content-wrapper {
  padding: 80px 20px 50px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.section-title {
  font-family: 'Gotham', sans-serif;
  font-size: 2.8rem;
  color: var(--color-primary);
  text-align: center;
  margin-bottom: 50px;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1);
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
  justify-items: center;
}

.product-card {
  background: var(--color-neutral);
  border-radius: 15px;
  padding: 15px;
  width: 100%;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden; /* Предотвращает вылезание */
  display: flex;
  flex-direction: column;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.product-link {
  text-decoration: none;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.product-image-container {
  width: 100%;
  height: 200px; /* Фиксированная высота */
  overflow: hidden;
  border-radius: 10px 10px 0 0;
}

.product-image-container img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Изображение полностью помещается */
  background: #f0f0f0;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image-container img {
  transform: scale(1.05);
}

.product-info {
  text-align: center;
  padding: 15px 0;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-info h3 {
  font-family: 'Gotham', sans-serif;
  font-size: 1.4rem;
  margin: 10px 0;
  color: var(--color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-info p {
  font-family: 'Candara', sans-serif;
  font-size: 1.3rem;
  color: var(--color-accent);
  font-weight: 600;
  margin: 0;
}

.water-decor {
  position: absolute;
  bottom: -40px;
  left: 0;
  width: 100%;
  opacity: 0.5;
  z-index: 1;
  filter: blur(3px);
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  z-index: 2;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--color-primary);
}

.error {
  color: #D9534F;
}

@media (max-width: 768px) {
  .hero-section {
    height: 350px;
  }

  .hero-content {
    padding: 20px;
    max-width: 90%;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.3rem;
  }

  .content-wrapper {
    padding: 60px 10px 30px;
  }

  .section-title {
    font-size: 2.2rem;
  }

  .product-grid {
    grid-template-columns: 1fr;
  }

  .product-image-container {
    height: 150px;
  }

  .product-info h3 {
    font-size: 1.2rem;
  }

  .product-info p {
    font-size: 1.1rem;
  }
}

/* Кастомизация тостов */
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
</style>