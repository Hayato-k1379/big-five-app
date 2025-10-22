<template>
  <v-app class="app-shell">
    <v-app-bar color="primary" density="comfortable" flat class="app-header">
      <v-app-bar-title class="app-title">Big Five 50問テスト</v-app-bar-title>
      <v-spacer />
      <RouterLink class="app-link" :to="{ name: 'survey' }">
        <v-btn variant="text" class="app-link__button">テストを開始</v-btn>
      </RouterLink>
    </v-app-bar>

    <v-main class="app-main">
      <router-view />
    </v-main>

    <AppFooter />
  </v-app>
</template>

<script setup>
import { RouterLink } from 'vue-router';
import AppFooter from './components/layout/Footer.vue';
</script>

<style scoped>
.app-shell {
  background-color: var(--app-background);
  color: var(--app-text);
  font-family: var(--app-font-family);
}

.app-header {
  color: #fff;
  background: linear-gradient(135deg, var(--app-accent), var(--app-accent-strong));
  letter-spacing: 0.08em;
}

.app-title {
  font-weight: 600;
  font-size: 1rem;
}

.app-main {
  background-color: transparent;
}

.app-link {
  text-decoration: none;
}

.app-link__button {
  color: #fff;
  text-transform: none;
  font-weight: 600;
  letter-spacing: 0.08em;
}
</style>
