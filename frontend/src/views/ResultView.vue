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
                <tr v-for="trait in result.trait_scores" :key="trait.trait">
                  <td>{{ trait.label }}</td>
                  <td class="text-right">{{ trait.sum }}</td>
                  <td class="text-right">{{ trait.scaled }}</td>
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
