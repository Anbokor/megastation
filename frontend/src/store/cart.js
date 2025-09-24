import { defineStore } from "pinia";
import { reactive } from "vue";
import { useToast } from "vue-toastification";

export const useCartStore = defineStore("cart", {
  state: () => {
    const items = reactive(JSON.parse(localStorage.getItem("cart")) || []);
    return { items };
  },
  getters: {
    totalItems: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    totalPrice: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0),
  },
  actions: {
    // FIX: Initialize toast once for all actions to use.
    // This prevents race conditions and duplicate notifications.
    _getToast() {
      if (!this._toast) {
        this._toast = useToast();
      }
      return this._toast;
    },
    addToCart(product) {
      const toast = this._getToast();
      try {
        const existing = this.items.find(item => item.id === product.id);
        if (existing) {
          existing.quantity++;
          toast.success("Cantidad aumentada en el carrito.");
        } else {
          this.items.push({ ...product, quantity: 1, availability: product.availability });
          toast.success("Producto añadido al carrito.");
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al añadir el producto al carrito.");
      }
    },
    increaseQuantity(productId) {
      const toast = this._getToast();
      try {
        const item = this.items.find(item => item.id === productId);
        if (item) {
          item.quantity++;
          toast.success("Cantidad aumentada.");
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al aumentar la cantidad.");
      }
    },
    decreaseQuantity(productId) {
      const toast = this._getToast();
      try {
        const item = this.items.find(item => item.id === productId);
        if (item && item.quantity > 1) {
          item.quantity--;
          toast.success("Cantidad reducida.");
        } else {
          this.removeFromCart(productId, { showToast: false }); // Avoid double toast
          toast.success("Producto eliminado del carrito.");
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al reducir la cantidad.");
      }
    },
    removeFromCart(productId, options = { showToast: true }) {
      const toast = this._getToast();
      try {
        const index = this.items.findIndex(item => item.id === productId);
        if (index !== -1) {
          this.items.splice(index, 1);
          if (options.showToast) {
            toast.success("Producto eliminado del carrito.");
          }
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al eliminar el producto.");
      }
    },
    clearCart() {
      const toast = this._getToast();
      try {
        this.items.length = 0;
        localStorage.removeItem("cart");
        toast.success("Carrito vaciado.");
      } catch (error) {
        toast.error("Error al vaciar el carrito.");
      }
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
