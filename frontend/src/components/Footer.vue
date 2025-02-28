<template>
  <footer class="footer">
    <p>© {{ new Date().getFullYear() }} Megastation - Todos los derechos reservados.</p>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
  color: var(--color-neutral);
  text-align: center;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
}
</style>