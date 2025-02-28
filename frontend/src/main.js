// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import axios from "axios";
import "./assets/styles.css";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faSearch, faBars, faShoppingCart, faSignInAlt, faSignOutAlt, faHome, faList, faUser, faLock, faEnvelope, faUserPlus } from "@fortawesome/free-solid-svg-icons";

// Add FontAwesome icons to library
library.add(faSearch, faBars, faShoppingCart, faSignInAlt, faSignOutAlt, faHome, faList, faUser, faLock, faEnvelope, faUserPlus);

axios.defaults.baseURL = "http://127.0.0.1:8000/";
axios.interceptors.request.use(config => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const app = createApp(App);
app.use(router);
app.use(createPinia());
app.component("font-awesome-icon", FontAwesomeIcon);
app.mount("#app");