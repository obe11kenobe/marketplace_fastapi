<template>
  <div class="wrap">
    <h1>404</h1>
    <p class="muted">Такой страницы нет.</p>
    <RouterLink to="/" class="btn">В каталог</RouterLink>
  </div>
</template>

<style scoped>
.wrap {
  padding: 80px 0;
  text-align: center;
}

h1 {
  font-size: 48px;
  margin: 0 0 8px;
}

p {
  margin: 0 0 24px;
}
</style>
