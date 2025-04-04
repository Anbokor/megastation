import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import Catalog from "@/views/Catalog.vue";
import Product from "@/views/Product.vue";
import Cart from "@/views/Cart.vue";
import Checkout from "@/views/Checkout.vue";
import Login from "@/views/Login.vue";
import Dashboard from "@/views/Dashboard.vue";
import Orders from "@/views/Orders.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/catalog", component: Catalog },
  { path: "/product/:id", component: Product },
  { path: "/cart", component: Cart },
  { path: "/checkout", component: Checkout },
  { path: "/login", component: Login },
  { path: "/dashboard", name: "Dashboard", component: Dashboard },
  { path: "/orders", name: "Orders", component: Orders },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;