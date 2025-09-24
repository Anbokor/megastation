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
        const response = await axios.post("/api/users/login/", credentials);
        this.token = response.data.access;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        await this.fetchUser(); // Fetch user data after login
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
        // Step 1: Attempt to register the new user.
        await axios.post("/api/users/register/", {
          username: userData.username,
          password: userData.password,
          email: userData.email,
          role: "customer",
        });

        // Step 2: If registration is successful, automatically log the user in.
        await this.login({ username: userData.username, password: userData.password });
        
        console.log("Registro y login automáticos exitosos");

      } catch (error) {
        // Step 3: Handle errors from either registration or the subsequent login attempt.
        let msg = "Ocurrió un error durante el registro.";
        if (error.response?.data) {
          // Flatten DRF error messages (e.g., {username: ["already exists"]}) into a single string.
          const errorMessages = Object.values(error.response.data).flat();
          if (errorMessages.length > 0) {
            msg = errorMessages.join(' ');
          }
        }
        console.error("Error en el proceso de registro:", error);
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
        this.logout(); // Log out if fetching user fails (e.g., expired token)
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
