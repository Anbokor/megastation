import { defineStore } from "pinia";
import axios from "axios";

export const useProductStore = defineStore("products", {
  state: () => ({
    products: [],
    categories: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchProducts() {
      this.loading = true;
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/store/products/");
        this.products = response.data;
      } catch (error) {
        this.error = "Error al cargar productos.";
      } finally {
        this.loading = false;
      }
    },

    async fetchCategories() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/store/categories/");
        this.categories = response.data;
      } catch (error) {
        console.error("❌ Error fetching categories:", error);
      }
    },
  },
});
