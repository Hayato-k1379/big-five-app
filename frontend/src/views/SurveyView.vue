<template>
  <v-container class="py-8" max-width="960">
    <v-alert type="error" v-if="error" class="mb-4">{{ error }}</v-alert>

    <v-sheet v-if="loading" class="py-12 d-flex justify-center">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-sheet>

    <template v-else>
      <v-card elevation="2">
        <v-card-title class="d-flex flex-column align-start">
          <h1 class="text-h5 font-weight-bold mb-2">50問に回答してビッグファイブ診断を受けましょう</h1>
          <p class="text-body-2 mb-0">すべて必須です。感じたままに5段階でお答えください。</p>
        </v-card-title>

        <v-card-text>
          <v-progress-linear
            :model-value="progress"
            color="primary"
            height="10"
            rounded
            class="mb-6"
          ></v-progress-linear>

          <small class="text-caption">回答済み {{ answeredCount }} / {{ totalItems }} 問 ({{ progress }}%)</small>

          <v-divider class="my-6"></v-divider>

          <v-form @submit.prevent="handleSubmit" class="survey-form">
            <div class="d-flex flex-column gap-6">
              <v-card
                v-for="item in items"
                :key="item.code"
                variant="outlined"
              >
                <v-card-text>
                  <div class="text-subtitle-1 font-weight-medium mb-4">{{ item.text }}</div>
                  <v-radio-group
                    v-model="responses[item.code]"
                    inline
                    class="likert-group"
                  >
                    <v-radio
                      v-for="choice in likertChoices"
                      :key="choice.value"
                      :label="choice.label"
                      :value="choice.value"
                    />
                  </v-radio-group>
                </v-card-text>
              </v-card>
            </div>

            <div class="action-buttons mt-8">
              <v-btn
                type="button"
                variant="outlined"
                color="secondary"
                :disabled="!totalItems || submitting"
                @click="fillRandomResponses"
              >
                ランダムに回答を埋める
              </v-btn>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="submitting"
                :disabled="!canSubmit"
              >
                診断結果を見る
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </template>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { apiClient, ensureArray } from '../lib/apiClient';

const router = useRouter();
const items = ref([]);
const responses = reactive({});
const loading = ref(true);
const submitting = ref(false);
const error = ref('');

const likertChoices = [
  { value: 1, label: 'まったく当てはまらない' },
  { value: 2, label: 'あまり当てはまらない' },
  { value: 3, label: 'どちらともいえない' },
  { value: 4, label: 'まあ当てはまる' },
  { value: 5, label: 'とても当てはまる' }
];

const totalItems = computed(() => items.value.length);
const answeredCount = computed(() =>
  Object.values(responses).filter((value) => value !== null && value !== undefined).length
);
const progress = computed(() => (totalItems.value ? Math.round((answeredCount.value / totalItems.value) * 100) : 0));
const canSubmit = computed(() => answeredCount.value === totalItems.value && totalItems.value > 0 && !submitting.value);

const fetchItems = async () => {
  loading.value = true;
  error.value = '';
  try {
    const { data } = await apiClient.get('items/');
    const normalizedItems = ensureArray(data, 'items response');
    items.value = normalizedItems;
    normalizedItems.forEach((item) => {
      responses[item.code] = null;
    });
  } catch (err) {
    console.error(err);
    error.value = '設問の取得に失敗しました。ページを更新して再試行してください。';
  } finally {
    loading.value = false;
  }
};

const fillRandomResponses = () => {
  if (!items.value.length) {
    return;
  }
  items.value.forEach((item) => {
    const randomValue = Math.floor(Math.random() * likertChoices.length) + 1;
    responses[item.code] = randomValue;
  });
};

const handleSubmit = async () => {
  if (!canSubmit.value) {
    return;
  }
  submitting.value = true;
  error.value = '';
  try {
    const payload = {};
    Object.entries(responses).forEach(([key, value]) => {
      payload[key] = Number(value);
    });
    const { data } = await apiClient.post('score/', { responses: payload });
    router.push({ name: 'result', params: { id: data.id }, state: { result: data } });
  } catch (err) {
    console.error(err);
    error.value = '結果の送信に失敗しました。時間をおいて再試行してください。';
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchItems();
});
</script>

<style scoped>
.likert-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 600px) {
  .action-buttons {
    flex-direction: row;
    align-items: center;
  }

  .action-buttons :deep(.v-btn) {
    width: auto;
  }
}
</style>
