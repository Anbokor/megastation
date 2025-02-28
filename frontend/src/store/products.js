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
        console.log("Продукты уже загружены, используется кэш");
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
        console.error("Ошибка загрузки продуктов:", error);
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
        this.currentProduct = null;
        console.error("Ошибка загрузки продукта:", error);
      } finally {
        this.loading = false;
      }
    },
    async fetchCategories() {
      if (this.categories.length > 0) {
        console.log("Категории уже загружены, используется кэш");
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
        console.error("Ошибка загрузки категорий:", error);
      } finally {
        this.loading = false;
      }
    },
  },
});