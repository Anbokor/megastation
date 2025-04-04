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
    addToCart(product) {
      const toast = useToast();

      try {
        const existing = this.items.find(item => item.id === product.id);
        if (existing) {
          existing.quantity++;
          toast.success("Cantidad aumentada en el carrito.", {
            toastClassName: "custom-toast-success",
          });
        } else {
          this.items.push({ ...product, quantity: 1, availability: product.availability });
          toast.success("Producto añadido al carrito.", {
            toastClassName: "custom-toast-success",
          });
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al añadir el producto al carrito.", {
          toastClassName: "custom-toast-error",
        });
      }
    },
    increaseQuantity(productId) {
      const toast = useToast();
      try {
        const item = this.items.find(item => item.id === productId);
        if (item) {
          item.quantity++;
          toast.success("Cantidad aumentada.", {
            toastClassName: "custom-toast-success",
          });
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al aumentar la cantidad.", {
          toastClassName: "custom-toast-error",
        });
      }
    },
    decreaseQuantity(productId) {
      const toast = useToast();
      try {
        const item = this.items.find(item => item.id === productId);
        if (item && item.quantity > 1) {
          item.quantity--;
          toast.success("Cantidad reducida.", {
            toastClassName: "custom-toast-success",
          });
        } else {
          this.removeFromCart(productId);
          toast.success("Producto eliminado por cantidad mínima.", {
            toastClassName: "custom-toast-success",
          });
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al reducir la cantidad.", {
          toastClassName: "custom-toast-error",
        });
      }
    },
    removeFromCart(productId) {
      const toast = useToast();
      try {
        const index = this.items.findIndex(item => item.id === productId);
        if (index !== -1) {
          this.items.splice(index, 1);
          toast.success("Producto eliminado del carrito.", {
            toastClassName: "custom-toast-success",
          });
        }
        this.saveCart();
      } catch (error) {
        toast.error("Error al eliminar el producto.", {
          toastClassName: "custom-toast-error",
        });
      }
    },
    clearCart() {
      const toast = useToast();
      try {
        this.items.length = 0;
        localStorage.removeItem("cart");
        toast.success("Carrito vaciado.", {
          toastClassName: "custom-toast-success",
        });
      } catch (error) {
        toast.error("Error al vaciar el carrito.", {
          toastClassName: "custom-toast-error",
        });
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