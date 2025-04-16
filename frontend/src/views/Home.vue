<script setup>
import { useRouter } from "vue-router";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";
import { onMounted, ref } from "vue";
import { useToast } from "vue-toastification";

const router = useRouter();
const productStore = useProductStore();
const cartStore = useCartStore();
const toast = useToast();
const visibleProducts = ref(new Set());

onMounted(async () => {
  try {
    await productStore.fetchProducts();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          visibleProducts.value.add(entry.target.dataset.id);
          observer.unobserve(entry.target);
        }
      });
    });
    document.querySelectorAll('.scroll-reveal').forEach((el) => {
      observer.observe(el);
    });
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

const addToCart = (product) => {
  cartStore.addToCart(product);
  toast.success("Producto añadido al carrito.", {
    toastClassName: "custom-toast-success",
  });
};
</script>

<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-background">
        <img src="@/assets/home-banner.jpg" alt="Banner Megastation" class="hero-image" loading="lazy" />
      </div>
      <div class="hero-content">
        <h1 class="hero-title">Bienvenido a Megastation</h1>
        <p class="hero-subtitle">Descubre lo último en tecnología</p>
        <button @click="goToCatalog" class="hero-button" title="Explorar catálogo">
          <span>Ver Catálogo</span>
          <div class="button-effect"></div>
        </button>
      </div>
    </div>

    <div class="content-wrapper">
      <h2 class="section-title scroll-reveal" :class="{ visible: visibleProducts.size > 0 }">
        Productos Populares
      </h2>

      <div v-if="productStore.loading" class="loading">
        <font-awesome-icon icon="spinner" spin /> Cargando...
      </div>

      <div v-else-if="productStore.error" class="error">
        {{ productStore.error }}
        <button @click="productStore.fetchProducts()">Reintentar</button>
      </div>

      <div v-else class="product-grid">
        <div
          v-for="(product, index) in productStore.products.slice(0, 4)"
          :key="product.id"
          class="product-card scroll-reveal"
          :class="{ visible: visibleProducts.has(String(product.id)) }"
          :data-id="product.id"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <router-link :to="'/product/' + product.id" class="product-link" :title="'Ver detalles de ' + product.name">
            <div class="product-image-container">
              <img
                :src="product.image_url || '/media/default_product.jpg'"
                :alt="product.name"
                loading="lazy"
              />
              <div class="image-overlay"></div>
            </div>
            <div class="product-info">
              <h3>{{ product.name }}</h3>
              <p class="price">$ {{ product.price }} <span class="underline"></span></p>
            </div>
          </router-link>
          <button
            @click="addToCart(product)"
            class="buy-now"
          >
            Comprar ahora
          </button>
        </div>
      </div>
    </div>

    <div class="decorative-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
  </div>
</template>

<style scoped>
:root {
  --color-primary: #2563eb;
  --color-secondary: #3b82f6;
  --color-accent: #60a5fa;
  --color-neutral: #ffffff;
  --color-text: #1f2937;
  --gradient-primary: linear-gradient(45deg, var(--color-primary), var(--color-accent));
  --transition-smooth: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.home {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
  position: relative;
  overflow: hidden;
}

.hero-section {
  position: relative;
  height: 80vh;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  perspective: 1000px;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.hero-background::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6));
  z-index: 2;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.7) saturate(1.2);
  transform: scale(1.1);
  transition: transform 8s ease;
}

.hero-section:hover .hero-image {
  transform: scale(1.2);
}

.hero-content {
  position: relative;
  z-index: 3;
  text-align: center;
  padding: 3rem 4rem;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transform: translateZ(50px);
  max-width: 800px;
  width: 90%;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.hero-title {
  font-size: clamp(2rem, 5vw, 4rem);
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.hero-subtitle {
  font-size: clamp(1.2rem, 3vw, 1.8rem);
  color: #e0e0e0;
  margin-bottom: 2rem;
  font-weight: 300;
  opacity: 0.9;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}

.hero-button {
  background: #ffffff;
  color: var(--color-primary);
  border: none;
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.hero-button:hover {
  transform: scale(1.05) translateY(-2px);
  background: #f0f0f0;
}

.button-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    transparent,
    rgba(0, 0, 0, 0.1),
    transparent
  );
  transition: 0.5s;
}

.hero-button:hover .button-effect {
  left: 100%;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 4rem 2rem;
  position: relative;
  z-index: 2;
}

.section-title {
  font-size: clamp(2rem, 4vw, 3rem);
  text-align: center;
  margin-bottom: 3rem;
  color: var(--color-text);
  font-weight: 800;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.product-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: var(--transition-smooth);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: none;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.product-image-container {
  position: relative;
  padding-top: 100%;
  overflow: hidden;
}

.product-image-container img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.5s ease;
}

.product-card:hover .product-image-container img {
  transform: scale(1.1);
}

.image-overlay {
  display: none;
}

.product-info {
  padding: 1rem;
  text-align: left;
}

.product-info h3 {
  font-size: 1.1rem;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.price {
  font-size: 1.2rem;
  color: var(--color-text);
  font-weight: 700;
  margin: 0.5rem 0;
  position: relative;
  display: inline-block;
}

.price .underline {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--color-accent);
}

.view-details {
  display: none;
}

.buy-now {
  background: #00c4ff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  margin: 0.5rem 1rem 1rem;
  transition: background 0.3s ease;
  font-size: 0.9rem;
  display: block;
  text-align: center;
}

.buy-now:hover {
  background: #00b0e6;
}

.decorative-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: var(--gradient-primary);
  opacity: 0.1;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: 20%;
  left: -100px;
}

.shape-3 {
  width: 150px;
  height: 150px;
  bottom: 10%;
  right: 20%;
}

.scroll-reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease-out;
}

.scroll-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 768px) {
  .hero-section {
    height: 60vh;
    min-height: 400px;
  }

  .hero-content {
    padding: 2rem;
    width: 95%;
  }

  .content-wrapper {
    padding: 2rem 1rem;
  }

  .product-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.loading {
  color: var(--color-primary);
}

.error {
  color: #ef4444;
}

:deep(.custom-toast-success) {
  background: var(--gradient-primary);
  border-radius: 10px;
}

:deep(.custom-toast-error) {
  background: linear-gradient(45deg, #ef4444, #f87171);
  border-radius: 10px;
}
</style>