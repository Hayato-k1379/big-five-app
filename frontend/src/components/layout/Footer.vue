<template>
  <v-footer app height="72" class="footer">
    <nav class="footer__nav">
      <a class="footer__link" :href="links.privacy">プライバシーポリシー</a>
      <span class="footer__separator">｜</span>
      <a class="footer__link" :href="links.terms">利用規約</a>
      <span class="footer__separator">｜</span>
      <a class="footer__link" :href="links.disclaimer">免責事項</a>
      <span class="footer__separator">｜</span>
      <a class="footer__link" :href="links.tokushoho">特定商取引法</a>
    </nav>
  </v-footer>
</template>

<script setup>
import { legalLinks } from '../../config/links.js';

const links = legalLinks;
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
