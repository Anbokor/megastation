<script setup>
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
</script>

<template>
  <div class="layout">
    <Header />
    <main class="content">
      <!-- Волна как декоративный элемент -->
      <svg class="wave-top" viewBox="0 0 1440 120">
        <path fill="var(--color-accent)" fill-opacity="0.4" d="M0,64L48,58.7C96,53,192,43,288,48C384,53,480,75,576,80C672,85,768,75,864,64C960,53,1056,43,1152,48C1248,53,1344,75,1392,85.3L1440,96L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"></path>
      </svg>
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-neutral);
  position: relative;
  overflow: hidden;
}

.wave-top {
  position: absolute;
  top: 60px; /* Под шапкой */
  left: 0;
  width: 100%;
  z-index: 0;
}

.content {
  flex: 1;
  padding: 90px 20px 20px 20px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1; /* Контент поверх волны */
}
</style>