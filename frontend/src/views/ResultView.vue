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
        <v-row>
          <v-col cols="12" md="6">
            <traits-radar-chart :trait-scores="result.trait_scores" />
          </v-col>
          <v-col cols="12" md="6">
            <v-table density="comfortable">
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
                      <span class="text-h6 font-weight-bold">{{ trait.scaled }}</span>
                      <v-chip
                        :color="trait.levelColor"
                        size="small"
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
        <p class="text-body-2 text-medium-emphasis mt-6">
          ID: {{ result.id }} ／ 診断日時: {{ formattedDate }}
        </p>
      </v-card-text>
    </v-card>
    <v-sheet
      v-if="result"
      elevation="1"
      class="mt-8 pa-6 d-flex flex-column align-center text-center"
    >
      <h2 class="text-h6 font-weight-bold mb-4">さらに詳しいフィードバックをチェック</h2>
      <v-btn
        color="primary"
        size="large"
        class="mb-2"
        :href="NOTE_DETAIL_PATH"
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
import axios from 'axios';
import TraitsRadarChart from '../components/TraitsRadarChart.vue';

const router = useRouter();
const route = useRoute();
const result = ref(null);
const loading = ref(true);
const error = ref('');

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
  if (score >= 66) {
    return { label: '高', color: 'success' };
  }
  if (score >= 33) {
    return { label: '中', color: 'warning' };
  }
  return { label: '低', color: 'info' };
};

const displayTraits = computed(() => {
  if (!result.value) {
    return [];
  }
  return result.value.trait_scores.map((trait) => {
    const level = getLevelInfo(trait.scaled);
    return {
      ...trait,
      levelLabel: level.label,
      levelColor: level.color
    };
  });
});

const fetchResult = async () => {
  loading.value = true;
  error.value = '';
  try {
    const { data } = await axios.get(`/api/results/${route.params.id}/`);
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
});
</script>
