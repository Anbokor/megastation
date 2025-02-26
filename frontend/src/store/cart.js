import { defineStore } from "pinia";

export const useCartStore = defineStore("cart", {
  state: () => ({
    items: JSON.parse(localStorage.getItem("cart")) || [],
  }),

  getters: {
    totalItems: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
  },

  actions: {
    addToCart(product) {
      const existingItem = this.items.find((item) => item.id === product.id);
      if (existingItem) {
        existingItem.quantity++;
      } else {
        this.items.push({ ...product, quantity: 1 });
      }
      this.saveCart();
    },

    removeFromCart(productId) {
      this.items = this.items.filter((item) => item.id !== productId);
      this.saveCart();
    },

    increaseQuantity(productId) {
      const item = this.items.find((item) => item.id === productId);
      if (item) {
        item.quantity++;
        this.saveCart();
      }
    },

    decreaseQuantity(productId) {
      const item = this.items.find((item) => item.id === productId);
      if (item && item.quantity > 1) {
        item.quantity--;
      } else {
        this.removeFromCart(productId);
      }
      this.saveCart();
    },

    clearCart() {
      this.items = [];
      localStorage.removeItem("cart");
    },

    saveCart() {
      localStorage.setItem("cart", JSON.stringify(this.items));
    },

    loadCart() {
      this.items = JSON.parse(localStorage.getItem("cart")) || [];
    },
  },
});
