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
        const response = await axios.post("/api/token/", credentials);
        this.token = response.data.access;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        await this.fetchUser();
      } catch (error) {
        console.error("Error en el inicio de sesión:", error);
      }
    },

    async fetchUser() {
      try {
        const response = await axios.get("/api/users/me/");
        this.user = response.data;
      } catch (error) {
        console.error("Error al obtener el usuario:", error);
        this.logout();
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
