import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/store/user";
import { useToast } from "vue-toastification";

// Import components
import Home from "@/views/Home.vue";
import Catalog from "@/views/Catalog.vue";
import Product from "@/views/Product.vue";
import Cart from "@/views/Cart.vue";
import Checkout from "@/views/Checkout.vue";
import Login from "@/views/Login.vue";
import Dashboard from "@/views/Dashboard.vue";
import Orders from "@/views/Orders.vue";
import StaffOrders from "@/views/StaffOrders.vue";
import StaffOrderDetail from "@/views/StaffOrderDetail.vue"; // Import the new component
import Profile from "@/views/Profile.vue";
import Invoices from "@/views/Invoices.vue";
import InvoiceCreate from "@/views/InvoiceCreate.vue";
import InvoiceDetail from "@/views/InvoiceDetail.vue";
import StockLevels from "@/views/StockLevels.vue";
import UserList from "@/views/UserList.vue";

const routes = [
  // Public routes
  { path: "/", name: "Home", component: Home },
  { path: "/catalog", name: "Catalog", component: Catalog },
  { path: "/product/:id", name: "Product", component: Product },
  { path: "/cart", name: "Cart", component: Cart },
  { path: "/login", name: "Login", component: Login },

  // Authenticated user routes (for all roles)
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: "/checkout",
    name: "Checkout",
    component: Checkout,
    meta: { requiresAuth: true },
  },
  {
    path: "/orders",
    name: "Orders",
    component: Orders,
    meta: { requiresAuth: true },
  },

  // Role-specific routes
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin'],
    },
  },
  {
    path: "/staff-orders",
    name: "StaffOrders",
    component: StaffOrders,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin', 'seller'],
    },
  },
  {
    path: "/staff/orders/:id", // Add the new route
    name: "StaffOrderDetail",
    component: StaffOrderDetail,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin', 'seller'],
    },
  },
  {
    path: "/invoices",
    name: "Invoices",
    component: Invoices,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin'],
    },
  },
  {
    path: "/invoices/create",
    name: "InvoiceCreate",
    component: InvoiceCreate,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin'],
    },
  },
  {
    path: "/invoices/:id",
    name: "InvoiceDetail",
    component: InvoiceDetail,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin'],
    },
  },
  {
    path: "/stock-levels",
    name: "StockLevels",
    component: StockLevels,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin', 'store_admin'],
    },
  },
  {
    path: "/users", // Add the user list route
    name: "UserList",
    component: UserList,
    meta: {
      requiresAuth: true,
      allowedRoles: ['superuser', 'admin'],
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard to check for authentication and authorization
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();
  const toast = useToast();

  // If user data is not loaded but a token exists, fetch it first.
  if (userStore.isAuthenticated && !userStore.getUser) {
    try {
      await userStore.fetchUser();
    } catch (error) {
      // fetchUser will handle logout on failure (e.g., expired token)
      // The guard will run again and redirect to login correctly.
      return next({ path: '/login', query: { redirect: to.fullPath } });
    }
  }

  const isAuthenticated = userStore.isAuthenticated;
  const userRole = userStore.getUser?.role;

  // 1. Check if the route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }

  // 2. Check if the route requires a specific role
  if (to.meta.allowedRoles && to.meta.allowedRoles.length > 0) {
    if (!isAuthenticated || !to.meta.allowedRoles.includes(userRole)) {
      toast.error("No tienes permiso para acceder a esta página.");
      return next({ path: '/' }); // Redirect to home page
    }
  }

  // 3. If all checks pass, proceed to the route
  next();
});

export default router;
