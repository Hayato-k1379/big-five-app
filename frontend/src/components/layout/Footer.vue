<template>
  <v-footer app height="72" class="footer">
    <nav class="footer__nav">
      <RouterLink class="footer__link" to="/privacy">プライバシーポリシー</RouterLink>
      <span class="footer__separator">｜</span>
      <RouterLink class="footer__link" to="/terms">利用規約</RouterLink>
      <span class="footer__separator">｜</span>
      <RouterLink class="footer__link" to="/disclaimer">免責事項</RouterLink>
      <span class="footer__separator">｜</span>
      <RouterLink class="footer__link" to="/legal/tokushoho">特定商取引法</RouterLink>
    </nav>
  </v-footer>
</template>

<script setup>
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.footer {
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  border-top: 1px solid var(--app-border);
  padding-block: var(--app-spacing-sm);
  color: var(--app-text-muted);
}

.footer__nav {
  display: flex;
  align-items: center;
  gap: var(--app-spacing-xs);
  font-size: 0.9rem;
  letter-spacing: 0.04em;
}

.footer__link {
  text-decoration: none;
  color: inherit;
  transition: color 160ms ease;
}

.footer__link:hover {
  color: var(--app-accent);
}

.footer__separator {
  color: var(--app-text-muted);
  opacity: 0.6;
}

@media (max-width: 480px) {
  .footer__nav {
    flex-wrap: wrap;
    justify-content: center;
    row-gap: 4px;
  }

  .footer__separator {
    display: none;
  }
}
</style>
