<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable" flat class="text-white">
      <v-app-bar-title>Big Five 50問テスト</v-app-bar-title>
      <v-spacer />
      <RouterLink class="app-link" :to="{ name: 'survey' }">
        <v-btn variant="text" class="text-white">テストを開始</v-btn>
      </RouterLink>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>

    <v-footer app height="72" class="d-flex align-center justify-center">
      <span>IPIPの項目はパブリックドメインです。</span>
    </v-footer>
  </v-app>
</template>

<script setup>
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.app-link {
  text-decoration: none;
}
</style>
