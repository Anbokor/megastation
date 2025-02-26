import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import Catalog from "@/views/Catalog.vue";
import Cart from "@/views/Cart.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/catalog", component: Catalog },
  { path: "/cart", component: Cart },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
