<script setup>
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
</script>

<template>
  <div class="layout">
    <!-- Light Animated Background -->
    <div class="background-container">
      <div class="shape shape1"></div>
      <div class="shape shape2"></div>
      <div class="shape shape3"></div>
      <div class="shape shape4"></div>
    </div>

    <Header />
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
  position: relative;
  overflow: hidden; /* Keep shapes contained */
  background-color: var(--color-background); /* Use the background color from the design system */
}

.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  animation: float 40s ease-in-out infinite;
}

.shape1 {
  width: 400px;
  height: 400px;
  background: var(--color-primary);
  top: -150px;
  left: -150px;
  animation-duration: 45s;
}

.shape2 {
  width: 500px;
  height: 500px;
  background: var(--color-secondary);
  bottom: -200px;
  right: -200px;
  animation-duration: 50s;
  animation-delay: -5s;
}

.shape3 {
  width: 300px;
  height: 300px;
  background: var(--color-primary);
  bottom: 100px;
  left: 10%;
  animation-duration: 55s;
  animation-delay: -10s;
}

.shape4 {
  width: 200px;
  height: 200px;
  background: var(--color-secondary);
  top: 10%;
  right: 5%;
  animation-duration: 60s;
  animation-delay: -15s;
}

@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-40px) rotate(180deg);
  }
  100% {
    transform: translateY(0px) rotate(360deg);
  }
}

.content {
  flex: 1;
  padding: 100px 20px 20px 20px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  position: relative; /* Ensure content is above the background */
  z-index: 1;
}
</style>
