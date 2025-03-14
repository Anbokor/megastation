import { defineStore } from "pinia";
import axios from "axios";

export const useProductStore = defineStore("products", {
  state: () => ({
    products: [],
    currentProduct: null,
    categories: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchProducts() {
      if (this.products.length > 0) {
        console.log("Productos ya cargados, utilizando caché");
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get("/api/store/products/");
        this.products = response.data;
      } catch (error) {
        this.error = error.response?.status === 429
          ? "Demasiadas solicitudes, espera un momento y recarga la página."
          : "Error al cargar productos.";
        console.error("Error al cargar productos:", error);
      } finally {
        this.loading = false;
      }
    },
    async fetchProduct(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`/api/store/products/${id}/`);
        this.currentProduct = response.data;
      } catch (error) {
        this.error = error.response?.status === 429
          ? "Demasiadas solicitudes, espera un momento."
          : "Error al cargar el producto.";
        console.error("Error al cargar el producto:", error);
        this.currentProduct = null;
      } finally {
        this.loading = false;
      }
    },
    async fetchCategories() {
      if (this.categories.length > 0) {
        console.log("Categorías ya cargadas, utilizando caché");
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get("/api/store/categories/");
        this.categories = response.data;
      } catch (error) {
        this.error = error.response?.status === 429
          ? "Demasiadas solicitudes, espera un momento y recarga la página."
          : "Error al cargar categorías.";
        console.error("Error al cargar categorías:", error);
      } finally {
        this.loading = false;
      }
    },
  },
});