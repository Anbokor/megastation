<script setup>
import { ref, computed, onMounted } from "vue";
import { useProductStore } from "@/store/products";
import { useCartStore } from "@/store/cart";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

const productStore = useProductStore();
const cartStore = useCartStore();
const route = useRoute();
const toast = useToast();
const selectedCategory = ref("");
const searchQuery = ref("");
const sortOption = ref("price_asc");

const filteredProducts = computed(() => {
  let products = [...productStore.products];
  if (selectedCategory.value) {
    products = products.filter(p => p.category_id === parseInt(selectedCategory.value));
  }
  if (searchQuery.value) {
    products = products.filter(p =>
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  switch (sortOption.value) {
    case "price_asc":
      products.sort((a, b) => {
        const priceA = Number(a.price) || 0; // Convert to number, default to 0 if invalid
        const priceB = Number(b.price) || 0;
        return priceA - priceB;
      });
      break;
    case "price_desc":
      products.sort((a, b) => {
        const priceA = Number(a.price) || 0;
        const priceB = Number(b.price) || 0;
        return priceB - priceA;
      });
      break;
    case "name_asc":
      products.sort((a, b) => a.name.localeCompare(b.name));
      break;
  }
  return products;
});

onMounted(async () => {
  try {
    if (!productStore.products.length) await productStore.fetchProducts();
    if (!productStore.categories.length) await productStore.fetchCategories();
    searchQuery.value = route.query.search || "";
  } catch (error) {
    toast.error("Error al cargar el catálogo.", {
      toastClassName: "custom-toast-error",
    });
  }
});

const addToCart = (product) => {
  if (product.availability === "available") {
    cartStore.addToCart(product);
  } else {
    toast.warning("Producto bajo pedido.", {
      toastClassName: "custom-toast-warning",
    });
  }
};
</script>

<template>
  <div class="catalog">
    <h1>📦 Catálogo de Productos</h1>
    <div class="filters">
      <input
        v-model="searchQuery"
        placeholder="Buscar productos..."
        title="Busca por nombre de producto"
      />
      <select v-model="selectedCategory" title="Filtra por categoría">
        <option value="">Todas las categorías</option>
        <option v-for="cat in productStore.categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <select v-model="sortOption" title="Ordenar productos">
        <option value="price_asc">Precio: Menor a Mayor</option>
        <option value="price_desc">Precio: Mayor a Menor</option>
        <option value="name_asc">Nombre (A-Z)</option>
      </select>
    </div>
    <div v-if="productStore.loading" class="loading">
      <font-awesome-icon icon="spinner" spin /> Cargando productos...
    </div>
    <div v-else-if="productStore.error" class="error">{{ productStore.error }}</div>
    <div v-else-if="filteredProducts.length === 0" class="empty">
      No hay productos disponibles.
    </div>
    <div v-else class="product-grid">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <router-link :to="'/product/' + product.id" class="product-link" :title="'Ver detalles de ' + product.name">
          <img :src="product.image_url || '/media/default_product.jpg'" :alt="product.name" />
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p>$ {{ product.price }}</p>
            <p :class="{ 'out-of-stock': product.availability === 'on_order' }">
              📦 {{ product.availability === "available" ? "Disponible" : "Bajo pedido" }}
            </p>
          </div>
        </router-link>
        <button
          @click="addToCart(product)"
          :disabled="product.availability === 'on_order'"
          class="add-btn"
          :title="product.availability === 'available' ? 'Añadir al carrito' : 'Producto no disponible'"
        >
          <font-awesome-icon icon="shopping-cart" /> {{ product.availability === "available" ? "Agregar" : "Bajo pedido" }}
        </button>
      </div>
    </div>
    <svg class="wave-bottom" viewBox="0 0 1440 120">
      <path
        fill="var(--color-primary)"
        fill-opacity="0.4"
        d="M0,64L48,58.7C96,53,192,43,288,48C384,53,480,75,576,80C672,85,768,75,864,64C960,53,1056,43,1152,48C1248,53,1344,75,1392,85.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
      ></path>
    </svg>
  </div>
</template>

<style scoped>
.catalog {
  padding: 20px;
  background: var(--color-neutral);
  position: relative;
  overflow: hidden;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

input,
select {
  padding: 12px;
  border: 1px solid var(--color-text);
  border-radius: 8px;
  font-family: 'Candara', sans-serif;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  background: #f9f9f9;
}

input:focus,
select:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 8px rgba(16, 164, 199, 0.3);
}

input {
  flex-grow: 1;
}

input::placeholder {
  color: #999;
  opacity: 0.8;
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
  padding: 20px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.product-link {
  text-decoration: none;
  color: var(--color-text);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.product-card img {
  max-width: 100%;
  height: 200px;
  border-radius: 10px;
  background: #f8f8f8;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover img {
  transform: scale(1.05);
}

.product-info {
  padding-top: 10px;
}

.product-info h3 {
  margin: 10px 0 5px;
  font-size: 1.2rem;
}

.product-info p {
  margin: 5px 0;
  font-size: 1.1rem;
}

.out-of-stock {
  color: #D9534F;
  font-weight: 500;
}

.add-btn {
  background: var(--color-primary);
  color: var(--color-neutral);
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
  margin-top: 10px;
  width: 100%;
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

.wave-bottom {
  position: absolute;
  bottom: -50px;
  left: 0;
  width: 100%;
  z-index: 0;
}

.loading,
.error,
.empty {
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

  .product-card img {
    height: 150px;
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