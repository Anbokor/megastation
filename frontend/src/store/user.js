import { defineStore } from "pinia";
import axios from "axios";

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token") || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user,
  },
  actions: {
    async login(credentials) {
      try {
        const response = await axios.post("/api/login/", credentials);
        this.token = response.data.access;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        // Убираем fetchUser, так как данных достаточно из токена
        // Если нужны данные позже, можно добавить опциональный вызов
      } catch (error) {
        let msg = "Credenciales inválidas. Verifica tu usuario y contraseña.";
        if (error.response && error.response.data && error.response.data.detail) {
          msg = error.response.data.detail;
        }
        throw new Error(msg);
      }
    },
    async register(userData) {
      try {
        const response = await axios.post("/api/register/", {
          username: userData.username,
          password: userData.password,
          email: userData.email,
          role: "customer",
        });
        this.token = response.data.access; // Используем access из ответа
        this.user = response.data.user; // Сохраняем данные пользователя из ответа
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        return response.data;
      } catch (error) {
        let msg = "Error al registrar. Verifica los datos.";
        if (error.response && error.response.data && error.response.data.detail) {
          msg = error.response.data.detail;
        }
        throw new Error(msg);
      }
    },
    // Оставляем fetchUser для будущего использования, если добавишь маршрут
    async fetchUser() {
      try {
        const response = await axios.get("/api/users/me/");
        this.user = response.data;
      } catch (error) {
        this.logout();
        throw new Error("No se pudo obtener los datos del usuario.");
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      delete axios.defaults.headers.common["Authorization"];
    },
  },
});