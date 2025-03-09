import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import axios from "axios";
import "./assets/styles.css";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faSearch, faBars, faShoppingCart, faSignInAlt, faSignOutAlt, faHome, faList, faUser, faLock, faEnvelope, faUserPlus, faPlus, faMinus, faTrash, faCreditCard, faStore, faSpinner } from "@fortawesome/free-solid-svg-icons";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

library.add(faSearch, faBars, faShoppingCart, faSignInAlt, faSignOutAlt, faHome, faList, faUser, faLock, faEnvelope, faUserPlus, faPlus, faMinus, faTrash, faCreditCard, faStore, faSpinner);

axios.defaults.baseURL = "http://127.0.0.1:8000/";
axios.interceptors.request.use(config => {
  const publicEndpoints = ["/api/store/products/", "/api/store/categories/"];
  const token = localStorage.getItem("token");
  if (token && !publicEndpoints.some(endpoint => config.url.includes(endpoint))) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const app = createApp(App);
app.use(router);
app.use(createPinia());
app.use(Toast, {
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
  maxToasts: 5,
  transition: "Vue-Toastification__bounce",
});
app.component("font-awesome-icon", FontAwesomeIcon);
app.mount("#app");