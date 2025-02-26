<script setup>
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
</script>

<template>
  <div class="layout">
    <Header /> <!-- ✅ Теперь шапка всегда отображается -->
    <main class="content">
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
}

.content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
