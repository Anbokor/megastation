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
        const response = await axios.post("/api/users/login/", credentials); // Исправлен эндпоинт
        this.token = response.data.access;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        await this.fetchUser(); // Добавляем загрузку данных после логина
        console.log("Inicio de sesión exitoso");
      } catch (error) {
        let msg = "Credenciales inválidas. Verifica tu usuario y contraseña.";
        if (error.response?.data?.detail) msg = error.response.data.detail;
        console.error("Error al iniciar sesión:", error);
        throw new Error(msg);
      }
    },
    async register(userData) {
      try {
        const response = await axios.post("/api/users/register/", {
          username: userData.username,
          password: userData.password,
          email: userData.email,
          role: "customer",
        });
        this.token = response.data.access;
        this.user = response.data.user;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        console.log("Registro exitoso");
        return response.data;
      } catch (error) {
        let msg = "Error al registrar. Verifica los datos.";
        if (error.response?.data?.detail) msg = error.response.data.detail;
        console.error("Error al registrar:", error);
        throw new Error(msg);
      }
    },
    async fetchUser() {
      try {
        if (!this.token) throw new Error("No hay token disponible");
        const response = await axios.get("/api/users/me/", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.user = response.data;
        console.log("Datos del usuario cargados:", this.user);
      } catch (error) {
        console.error("Error al cargar datos del usuario:", error.response?.data || error.message);
        this.logout();
        throw new Error("No se pudo obtener los datos del usuario.");
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      delete axios.defaults.headers.common["Authorization"];
      console.log("Sesión cerrada");
    },
  },
});