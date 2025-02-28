<script setup>
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
</script>

<template>
  <div class="layout">
    <Header />
    <main class="content">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<style scoped>
/* Enhanced layout with subtle wave effect */
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(to bottom, rgba(16, 164, 199, 0.2), #FFFFFF);
  position: relative;
  overflow: hidden;
}

.layout::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, var(--color-accent), transparent);
  opacity: 0.3;
  z-index: -1;
}

.content {
  flex: 1;
  padding: 90px 20px 20px 20px; /* Отступ сверху для фиксированной шапки */
  max-width: 1200px;
  margin: 0 auto;
}
</style>