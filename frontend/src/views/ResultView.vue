<template>
  <v-container class="py-8" max-width="960">
    <v-btn variant="text" prepend-icon="mdi-arrow-left" class="mb-4" @click="goBack">
      設問一覧に戻る
    </v-btn>

    <v-alert type="error" v-if="error" class="mb-4">{{ error }}</v-alert>

    <v-sheet v-if="loading" class="py-12 d-flex justify-center">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-sheet>

    <v-card v-else-if="result" elevation="2">
      <v-card-title class="d-flex flex-column align-start">
        <h1 class="text-h5 font-weight-bold mb-2">診断結果</h1>
        <p class="text-body-2 mb-0">各特性の合計値（最大{{ result.scaled_range.max }}）と0〜100スケール換算です。</p>
      </v-card-title>
      <v-card-text>
        <v-row class="gy-6">
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
        <section v-if="highlightCards.length" class="highlight-section mt-8">
          <h2 class="text-subtitle-1 font-weight-bold mb-4">特性ハイライト</h2>
          <v-row class="gy-4 highlight-row">
            <v-col v-for="card in highlightCards" :key="card.key" cols="12" md="6">
              <v-card
                variant="outlined"
                class="highlight-card pa-4"
                :style="getHighlightAccentStyle(card.color)"
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
              </v-card>
            </v-col>
          </v-row>
        </section>
        <p class="text-body-2 text-medium-emphasis mt-6">
          ID: {{ result.id }} ／ 診断日時: {{ formattedDate }}
        </p>
      </v-card-text>
    </v-card>
    <v-sheet
      v-if="result"
      elevation="1"
      :class="[
        'mt-8 d-flex flex-column align-center text-center cta-sheet',
        isMobile ? 'pa-5' : 'pa-6'
      ]"
    >
      <h2 class="text-h6 font-weight-bold mb-4">さらに詳しいフィードバックをチェック</h2>
      <v-btn
        color="primary"
        size="large"
        class="mb-2"
        :href="NOTE_DETAIL_PATH"
        :block="isMobile"
      >
        詳細結果（¥500）
      </v-btn>
      <p class="text-body-2 text-medium-emphasis mb-0">
        ※ 有料記事（note）に移動します。購入後は記事内の「アプリに戻る」リンクから本ページに戻れます。
      </p>
    </v-sheet>
    <v-alert v-else type="warning">結果が見つかりませんでした。</v-alert>
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
  return result.value.trait_scores.map((trait) => {
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

const fetchResult = async () => {
  loading.value = true;
  error.value = '';
  try {
    const { data } = await apiClient.get(`results/${route.params.id}/`);
    result.value = data;
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
.cta-sheet {
  width: 100%;
  max-width: 720px;
  margin-inline: auto;
}

.result-table :deep(thead th) {
  white-space: nowrap;
}

.result-table :deep(td) {
  vertical-align: middle;
}

.highlight-section {
  width: 100%;
  padding-inline: 12px;
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
  background-color: var(--highlight-accent, var(--v-theme-primary));
  border-top-left-radius: inherit;
  border-bottom-left-radius: inherit;
}

@media (max-width: 599px) {
  .cta-sheet {
    max-width: 100%;
  }

  .highlight-section {
    padding-inline: 8px;
  }

  .highlight-row :deep(.v-col) {
    padding-inline: 8px;
  }

  .result-table :deep(td) {
    padding-block: 12px;
  }
}
</style>
