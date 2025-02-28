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
        await this.fetchUser();
      } catch (error) {
        throw error;
      }
    },
    async register(userData) {
      try {
        // Фиксируем роль как customer для всех регистраций через фронт
        const response = await axios.post("/api/register/", {
          username: userData.username,
          password: userData.password,
          email: userData.email,
          role: "customer"  // Фиксируем роль customer
        });
        this.token = response.data.token;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        this.user = response.data.user;
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    async fetchUser() {
      try {
        const response = await axios.get("/api/users/me/");
        this.user = response.data;
      } catch (error) {
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