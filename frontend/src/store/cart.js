import { defineStore } from "pinia";
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "./user";

export const useCartStore = defineStore("cart", {
  state: () => ({
    items: reactive(JSON.parse(localStorage.getItem("cart")) || []),
  }),
  getters: {
    totalItems: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    totalPrice: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0),
  },
  actions: {
    addToCart(product) {
      const userStore = useUserStore();
      const router = useRouter();

      if (!userStore.isAuthenticated) {
        alert("Por favor, inicia sesión o regístrate para añadir productos al carrito.");
        router.push("/login");
        return;
      }

      const existing = this.items.find(item => item.id === product.id);
      if (existing) existing.quantity++;
      else this.items.push({ ...product, quantity: 1 });
      this.saveCart();
    },
    increaseQuantity(productId) {
      const item = this.items.find(item => item.id === productId);
      if (item) item.quantity++;
      this.saveCart();
    },
    decreaseQuantity(productId) {
      const item = this.items.find(item => item.id === productId);
      if (item && item.quantity > 1) item.quantity--;
      else this.removeFromCart(productId);
      this.saveCart();
    },
    removeFromCart(productId) {
      this.items = this.items.filter(item => item.id !== productId);
      this.saveCart();
    },
    clearCart() {
      this.items.length = 0;
      localStorage.removeItem("cart");
    },
    saveCart() {
      localStorage.setItem("cart", JSON.stringify(this.items));
    },
    loadCart() {
      const saved = JSON.parse(localStorage.getItem("cart")) || [];
      this.items.length = 0;
      saved.forEach(item => this.items.push(item));
    },
  },
});