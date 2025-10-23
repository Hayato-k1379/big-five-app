<template>
  <v-container class="result-container" max-width="960">
    <v-btn variant="text" prepend-icon="mdi-arrow-left" class="mb-4" @click="goBack">
      設問一覧に戻る
    </v-btn>

    <v-alert type="error" v-if="error" class="mb-4">{{ error }}</v-alert>

    <v-sheet v-if="loading" class="result-loading">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-sheet>

    <v-card v-else-if="result" elevation="0" class="result-card">
      <v-card-title class="result-card__header">
        <h1 class="result-title">人は、見つめることで変わっていく。</h1>
        <p class="result-subtitle">各特性の輪郭を静かに読み解き、今のあなたの姿を写し取ります。</p>
      </v-card-title>
      <v-card-text class="result-card__body">
        <v-row class="gy-6 result-grid">
          <v-col cols="12" class="d-flex justify-center">
            <traits-radar-chart :trait-scores="result.trait_scores" class="w-100" />
          </v-col>
          <v-col cols="12">
            <v-table :density="tableDensity" class="result-table">
              <thead>
                <tr>
                  <th>特性</th>
                  <th class="text-right">合計</th>
                  <th class="text-right">スコア</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trait in displayTraits" :key="trait.trait">
                  <td>{{ trait.label }}</td>
                  <td class="text-right">{{ trait.sum }}</td>
                  <td class="text-right">
                    <div class="d-flex align-center justify-end" style="gap: 8px;">
                      <span :class="[scoreTextClass, 'font-weight-bold']">{{ trait.displayScore }}</span>
                      <v-chip
                        :color="trait.levelColor"
                        :size="chipSize"
                        variant="flat"
                        class="text-body-2 font-weight-medium"
                      >
                        {{ trait.levelLabel }}
                      </v-chip>
                    </div>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-col>
        </v-row>
        <section v-if="highlightCards.length" class="highlight-section">
          <h2 class="highlight-title">特性ハイライト</h2>
          <v-row class="gy-4 highlight-row">
            <v-col v-for="card in highlightCards" :key="card.key" cols="12" md="6">
              <v-card
                variant="outlined"
                class="highlight-card pa-4"
                :style="getHighlightAccentStyle(card.color)"
                @click="openTraitDetail(item, card.title)"
                role="button"
                tabindex="0"
                @keydown.enter.prevent="openTraitDetail(item, card.title)"
              >
                <div class="d-flex align-center mb-3" style="gap: 12px;">
                  <v-chip
                    v-if="card.badge"
                    :color="card.color"
                    variant="flat"
                    size="small"
                    class="highlight-chip font-weight-medium"
                  >
                    {{ card.badge }}
                  </v-chip>
                  <span class="text-subtitle-1 font-weight-medium">{{ card.title }}</span>
                </div>
                <div class="d-flex flex-column" style="gap: 8px;">
                  <div
                    v-for="item in card.traits"
                    :key="item.trait"
                    class="d-flex align-center justify-space-between highlight-trait-row"
                  >
                    <span class="text-body-1 font-weight-medium">{{ item.label }}</span>
                    <span class="text-subtitle-1 font-weight-bold">{{ item.display_score }}</span>
                  </div>
                </div>
                <div class="highlight-card__overlay">
                  <span>詳細を見る</span>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </section>
        <p class="result-meta">
          ID: {{ result.id }} ／ 診断日時: {{ formattedDate }}
        </p>
      </v-card-text>
    </v-card>
    <v-sheet
      v-if="result"
      elevation="1"
      :class="[
        'cta-sheet',
        isMobile ? 'pa-5' : 'pa-6'
      ]"
    >
      <h2 class="cta-title">構造を持てば、希望は形になる。</h2>
      <v-btn
        color="primary"
        size="large"
        class="mb-2"
        :href="NOTE_DETAIL_PATH"
        :block="isMobile"
      >
        詳細結果（¥500）
      </v-btn>
      <p class="cta-note">
        ※ 有料記事（note）に移動します。購入後は記事内の「アプリに戻る」リンクから本ページに戻れます。
      </p>
    </v-sheet>
    <v-alert v-else type="warning">結果が見つかりませんでした。</v-alert>

    <v-dialog v-model="detailDialog" max-width="520" scrollable>
      <v-card class="detail-dialog">
        <v-card-title class="detail-dialog__title">
          <div class="detail-dialog__labels">
            <span class="detail-dialog__eyebrow">{{ selectedTrait?.title }}</span>
            <h3>{{ selectedTrait?.label }}</h3>
          </div>
          <v-btn icon="mdi-close" variant="text" @click="closeTraitDetail" />
        </v-card-title>
        <v-card-text class="detail-dialog__body">
          <div class="detail-dialog__score">スコア: {{ selectedTrait?.score ?? '―' }}</div>
          <p class="detail-dialog__description">{{ selectedTrait?.description }}</p>
        </v-card-text>
        <v-card-actions class="detail-dialog__actions">
          <v-btn color="primary" block @click="closeTraitDetail">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiClient } from '../lib/apiClient';
import TraitsRadarChart from '../components/TraitsRadarChart.vue';
import { useDisplay } from 'vuetify';

const router = useRouter();
const route = useRoute();
const result = ref(null);
const loading = ref(true);
const error = ref('');
const display = useDisplay();
const detailDialog = ref(false);
const selectedTrait = ref(null);

const goBack = () => {
  router.push({ name: 'survey' });
};

const formattedDate = computed(() => {
  if (!result.value) {
    return '';
  }
  const date = new Date(result.value.created_at);
  return date.toLocaleString('ja-JP');
});

const loadFromHistoryState = () => {
  const state = window.history.state;
  if (state && state.result && state.result.id === route.params.id) {
    result.value = state.result;
  }
};

const NOTE_DETAIL_PATH = '/go/note-detail/';

const getLevelInfo = (score) => {
  if (score >= 60) {
    return { label: '強', color: 'success' };
  }
  if (score <= 40) {
    return { label: '弱', color: 'indigo' };
  }
  return { label: '中', color: 'secondary' };
};

const isMobile = computed(() => display.smAndDown.value);
const tableDensity = computed(() => (isMobile.value ? 'compact' : 'comfortable'));
const chipSize = computed(() => (isMobile.value ? 'small' : 'default'));
const scoreTextClass = computed(() => (isMobile.value ? 'text-subtitle-1' : 'text-h6'));

const getHighlightAccentStyle = (color) => ({
  '--highlight-accent': `var(--v-theme-${color ?? 'primary'})`
});

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const displayTraits = computed(() => {
  if (!result.value) {
    return [];
  }
  const traitSource = Array.isArray(result.value.trait_scores) ? result.value.trait_scores : [];
  if (!Array.isArray(result.value.trait_scores)) {
    console.error('[ResultView] trait_scores is not an array', result.value.trait_scores);
  }
  return traitSource.map((trait) => {
    const displayScore = trait.display_score ?? trait.scaled;
    const level = getLevelInfo(displayScore);
    return {
      ...trait,
      displayScore,
      levelLabel: level.label,
      levelColor: level.color
    };
  });
});

const highlightCards = computed(() => {
  const data = result.value?.highlights;
  if (!data) {
    return [];
  }

  const cards = [];

  if (data.signature_strength) {
    cards.push({
      key: 'signature_strength',
      title: '代表特性（強）',
      badge: '強',
      color: 'success',
      traits: [data.signature_strength]
    });
  }

  if (data.signature_caution) {
    cards.push({
      key: 'signature_caution',
      title: '代表特性（弱）',
      badge: '弱',
      color: 'indigo',
      traits: [data.signature_caution]
    });
  }

  if (Array.isArray(data.strong_candidates) && data.strong_candidates.length) {
    cards.push({
      key: 'strong_candidates',
      title: '強 候補',
      badge: null,
      color: 'success',
      traits: data.strong_candidates
    });
  }

  if (Array.isArray(data.weak_candidates) && data.weak_candidates.length) {
    cards.push({
      key: 'weak_candidates',
      title: '弱 候補',
      badge: null,
      color: 'indigo',
      traits: data.weak_candidates
    });
  }

  return cards;
});

const openTraitDetail = (trait, cardTitle) => {
  selectedTrait.value = {
    title: cardTitle,
    label: trait.label,
    score: trait.display_score ?? trait.scaled ?? trait.sum,
    description:
      trait.description
      ?? trait.detail
      ?? trait.long_text
      ?? trait.summary
      ?? 'この特性に関する詳細な説明は現在準備中です。'
  };
  detailDialog.value = true;
};

const closeTraitDetail = () => {
  detailDialog.value = false;
  selectedTrait.value = null;
};

const normalizeResultPayload = (payload) => {
  if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
    return payload;
  }
  console.error('[ResultView] Unexpected result payload', payload);
  return null;
};

const fetchResult = async () => {
  loading.value = true;
  error.value = '';
  try {
    const { data } = await apiClient.get(`results/${route.params.id}/`);
    const normalized = normalizeResultPayload(data);
    if (!normalized) {
      error.value = '結果データの取得形式が不正でした。時間をおいて再試行してください。';
      result.value = null;
      return;
    }
    result.value = normalized;
  } catch (err) {
    console.error(err);
    error.value = '結果の取得に失敗しました。URLをご確認のうえ再試行してください。';
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  loadFromHistoryState();
  if (!result.value) {
    await fetchResult();
  } else {
    loading.value = false;
  }
  scrollToTop();
});
</script>

<style scoped>
.result-container {
  padding-block: var(--app-spacing-xl);
  padding-inline: clamp(var(--app-spacing-sm), 4vw, var(--app-spacing-xl));
  color: var(--app-text);
}

.result-loading {
  display: flex;
  justify-content: center;
  padding-block: calc(var(--app-spacing-xl) - 8px);
  background: transparent;
}

.result-card {
  background-color: var(--app-surface);
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-soft);
  overflow: hidden;
}

.result-card__header {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-sm);
  padding: var(--app-spacing-lg);
  background: linear-gradient(135deg, rgba(195, 74, 44, 0.14), rgba(247, 244, 239, 0.96));
}

.result-title {
  margin: 0;
  font-size: clamp(1.5rem, 2vw + 1rem, 2.25rem);
  font-weight: 600;
  color: var(--app-headline);
}

.result-subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: var(--app-text-muted);
}

.result-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-lg);
  padding: var(--app-spacing-lg);
}

.result-grid {
  margin: 0;
}

.result-table {
  border-radius: var(--app-radius-md);
  border: 1px solid var(--app-border);
  overflow: hidden;
}

.result-table :deep(thead th) {
  white-space: nowrap;
  background-color: var(--app-surface-muted);
  color: var(--app-headline);
}

.result-table :deep(td) {
  vertical-align: middle;
  color: var(--app-text);
}

.result-table :deep(tr:nth-child(even) td) {
  background-color: rgba(240, 235, 228, 0.5);
}

.highlight-section {
  width: 100%;
  margin-top: var(--app-spacing-lg);
}

.highlight-title {
  margin: 0 0 var(--app-spacing-md);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--app-headline);
}

.highlight-row {
  margin: 0 !important;
}

.highlight-row :deep(.v-col) {
  padding-inline: 12px;
}

.highlight-card {
  position: relative;
  height: 100%;
  overflow: hidden;
  border-color: var(--app-border);
  border-radius: var(--app-radius-md);
  background-color: var(--app-surface);
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.highlight-chip {
  letter-spacing: 0.12em;
}

.highlight-trait-row {
  padding-block: 6px;
}

.highlight-card::before {
  content: '';
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: 6px;
  background-color: var(--highlight-accent, var(--app-accent));
  border-top-left-radius: inherit;
  border-bottom-left-radius: inherit;
}

.highlight-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--app-shadow-soft);
}

.highlight-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(140deg, rgba(195, 74, 44, 0.08), rgba(247, 244, 239, 0.92));
  opacity: 0;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 16px;
  color: var(--app-accent-strong);
  font-size: 0.85rem;
  letter-spacing: 0.12em;
  pointer-events: none;
  transition: opacity 160ms ease;
}

.highlight-card:hover .highlight-card__overlay,
.highlight-card:focus-visible .highlight-card__overlay {
  opacity: 1;
}

.result-meta {
  margin-top: var(--app-spacing-md);
  color: var(--app-text-muted);
  font-size: 0.85rem;
}

.cta-sheet {
  width: 100%;
  max-width: 720px;
  margin: var(--app-spacing-xl) auto 0;
  border-radius: calc(var(--app-radius-lg) - 4px);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-soft);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--app-spacing-sm);
}

.cta-title {
  margin: 0;
  font-size: clamp(1.25rem, 1.2rem + 1vw, 1.75rem);
  font-weight: 600;
  color: var(--app-headline);
}

.cta-note {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 0.85rem;
}

.cta-sheet :deep(.v-btn) {
  text-transform: none;
  letter-spacing: 0.08em;
  border-radius: var(--app-radius-sm);
  min-width: 220px;
}

@media (max-width: 599px) {
  .result-container {
    padding-inline: var(--app-spacing-sm);
  }

  .highlight-row :deep(.v-col) {
    padding-inline: 8px;
  }

  .result-table :deep(td) {
    padding-block: 12px;
  }
}

@media (min-width: 960px) {
  .result-card__body {
    padding: calc(var(--app-spacing-xl) - 4px);
  }
}

.detail-dialog {
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-soft);
  background: var(--app-surface);
}

.detail-dialog__title {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--app-spacing-sm);
}

.detail-dialog__labels {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-dialog__eyebrow {
  font-size: 0.8rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-text-muted);
}

.detail-dialog__labels h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.detail-dialog__body {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-sm);
  color: var(--app-text);
}

.detail-dialog__score {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--app-accent-strong);
}

.detail-dialog__description {
  margin: 0;
  line-height: 1.7;
}

.detail-dialog__actions {
  padding: var(--app-spacing-md);
}
</style>
