<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="home">
    <h1>Bienvenido a Megastation</h1>
    <p>Explora nuestra selección de productos electrónicos.</p>
    <button @click="router.push('/catalog')">Ver Catálogo</button>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 50px;
}

button {
  background-color: var(--color-accent);
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 10px;
}

button:hover {
  background-color: var(--color-accent-hover);
}
</style>
