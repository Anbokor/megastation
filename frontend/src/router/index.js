import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import Catalog from "@/views/Catalog.vue";
import Cart from "@/views/Cart.vue";
import Checkout from "@/views/Checkout.vue";
import ProductDetail from "@/views/ProductDetail.vue";
import Login from "@/views/Login.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/catalog", component: Catalog },
  { path: "/cart", component: Cart },
  { path: "/checkout", component: Checkout },
  { path: "/product/:id", component: ProductDetail },
  { path: "/login", component: Login },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
