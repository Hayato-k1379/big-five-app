<template>
  <v-container class="survey-container" max-width="960">
    <v-alert type="error" v-if="error" class="mb-4">{{ error }}</v-alert>

    <v-sheet v-if="loading" class="py-12 d-flex justify-center">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-sheet>

    <template v-else>
      <v-card elevation="0" class="survey-card">
        <v-card-title class="survey-card__header">
          <h1 class="survey-title">静けさの中で、自分を観察する時間を。</h1>
          <p class="survey-subtitle">50の問いを通じて、今のあなたを静かに映し出します。すべて必須です。</p>
        </v-card-title>

        <v-card-text class="survey-card__body">
          <v-progress-linear
            :model-value="progress"
            color="primary"
            height="10"
            rounded
            class="survey-progress"
          ></v-progress-linear>

          <small class="survey-progress__label">回答済み {{ answeredCount }} / {{ totalItems }} 問 ({{ progress }}%)</small>

          <div class="survey-stepper" v-if="items.length">
            <button
              v-for="(item, index) in items"
              :key="item.code"
              type="button"
              class="stepper-dot"
              :class="{
                'is-active': index === currentIndex,
                'is-answered': responses[item.code] !== null && responses[item.code] !== undefined
              }"
              @click="goToIndex(index)"
            >
              {{ index + 1 }}
            </button>
          </div>

          <v-divider class="survey-divider"></v-divider>

          <v-form @submit.prevent="handleSubmit" class="survey-form">
            <div ref="wizardRef" class="survey-wizard">
              <transition name="wizard-slide" mode="out-in">
                <v-card
                  v-if="currentItem"
                  :key="currentItem.code"
                  variant="outlined"
                  class="survey-item-card wizard-card"
                >
                  <v-card-text class="survey-item-card__body">
                    <div class="wizard-meta">
                      <span class="wizard-step">第 {{ currentIndex + 1 }} 問 / {{ totalItems }}</span>
                      <span
                        v-if="responses[currentItem.code] !== null && responses[currentItem.code] !== undefined"
                        class="wizard-status"
                      >
                        回答済み
                      </span>
                    </div>
                    <div class="survey-question">{{ currentItem.text }}</div>
                    <v-radio-group
                      v-model="responses[currentItem.code]"
                      :class="['likert-group', { 'likert-group--wide': isWide }]"
                      @update:modelValue="(value) => handleChoice(currentItem.code, value)"
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
              </transition>
            </div>

            <div class="wizard-nav">
              <v-btn
                type="button"
                variant="text"
                color="secondary"
                :disabled="isFirst"
                @click="goPrev"
              >
                前へ
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                type="button"
                variant="text"
                color="secondary"
                :disabled="!hasUnansweredAhead"
                @click="goNextUnanswered"
              >
                未回答に移動
              </v-btn>
              <v-btn
                type="button"
                variant="text"
                color="secondary"
                :disabled="isLast"
                @click="goNext"
              >
                次へ
              </v-btn>
            </div>

            <v-divider class="survey-divider"></v-divider>

            <div class="action-buttons">
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplay } from 'vuetify';
import { apiClient, ensureArray } from '../lib/apiClient';

const router = useRouter();
const display = useDisplay();
const items = ref([]);
const responses = reactive({});
const loading = ref(true);
const submitting = ref(false);
const error = ref('');
const currentIndex = ref(0);
const wizardRef = ref(null);

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
const isWide = computed(() => display.mdAndUp.value);
const currentItem = computed(() => items.value[currentIndex.value] || null);
const isFirst = computed(() => currentIndex.value === 0);
const isLast = computed(() => !totalItems.value || currentIndex.value >= totalItems.value - 1);
const hasUnansweredAhead = computed(() => findNextUnansweredIndex(currentIndex.value + 1) !== -1);

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
    currentIndex.value = 0;
    await nextTick();
    scrollToCurrent();
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
  currentIndex.value = 0;
  scrollToCurrent();
};

const scrollToCurrent = () => {
  nextTick(() => {
    if (wizardRef.value) {
      wizardRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
};

const findNextUnansweredIndex = (startIndex = 0) => {
  for (let i = startIndex; i < items.value.length; i += 1) {
    const item = items.value[i];
    if (responses[item.code] === null || responses[item.code] === undefined) {
      return i;
    }
  }
  return -1;
};

const goToIndex = (index) => {
  if (index < 0 || index >= totalItems.value) {
    return;
  }
  currentIndex.value = index;
  scrollToCurrent();
};

const goNext = () => {
  if (isLast.value) {
    return;
  }
  goToIndex(currentIndex.value + 1);
};

const goPrev = () => {
  if (isFirst.value) {
    return;
  }
  goToIndex(currentIndex.value - 1);
};

const goNextUnanswered = () => {
  const next = findNextUnansweredIndex(currentIndex.value + 1);
  if (next !== -1) {
    goToIndex(next);
  }
};

const autoAdvanceAfterAnswer = () => {
  const nextUnanswered = findNextUnansweredIndex(currentIndex.value + 1);
  if (nextUnanswered !== -1) {
    goToIndex(nextUnanswered);
  } else if (!isLast.value) {
    goNext();
  }
};

const handleChoice = (code, value) => {
  responses[code] = Number(value);
  autoAdvanceAfterAnswer();
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

const handleKeydown = (event) => {
  if (event.defaultPrevented) {
    return;
  }
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
    return;
  }
  if (event.key === 'ArrowRight') {
    event.preventDefault();
    goNext();
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault();
    goPrev();
  }
};

onMounted(() => {
  fetchItems();
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});

watch(totalItems, (count) => {
  if (count) {
    currentIndex.value = 0;
    scrollToCurrent();
  }
});
</script>

<style scoped>
.survey-container {
  padding-block: var(--app-spacing-xl);
  padding-inline: clamp(var(--app-spacing-sm), 4vw, var(--app-spacing-lg));
}

.survey-card {
  background-color: var(--app-surface);
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-soft);
}

.survey-card__header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--app-spacing-sm);
  padding: var(--app-spacing-lg);
  background: linear-gradient(135deg, rgba(195, 74, 44, 0.12), rgba(247, 244, 239, 0.92));
}

.survey-title {
  margin: 0;
  font-size: clamp(1.5rem, 2vw + 1rem, 2.25rem);
  font-weight: 600;
  color: var(--app-headline);
}

.survey-subtitle {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 0.95rem;
}

.survey-card__body {
  padding: var(--app-spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-md);
}

.survey-progress {
  margin-bottom: var(--app-spacing-sm);
  background-color: var(--app-accent-soft);
}

.survey-progress__label {
  color: var(--app-text-muted);
}

.survey-divider {
  margin-block: var(--app-spacing-md);
}

.survey-stepper {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--app-spacing-sm);
}

.stepper-dot {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--app-border);
  background-color: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 200ms ease;
}

.stepper-dot.is-answered {
  border-color: rgba(195, 74, 44, 0.35);
  background: rgba(195, 74, 44, 0.12);
  color: var(--app-accent-strong);
  box-shadow: 0 0 0 6px rgba(195, 74, 44, 0.08);
}

.stepper-dot.is-active {
  background: var(--app-accent);
  color: #fff;
  border-color: var(--app-accent-strong);
  box-shadow: 0 0 0 6px rgba(195, 74, 44, 0.2);
}

.survey-wizard {
  min-height: 280px;
  display: flex;
  flex-direction: column;
}

.wizard-card {
  flex: 1;
  background: var(--app-surface);
}

.wizard-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--app-spacing-xs);
  color: var(--app-text-muted);
  font-size: 0.9rem;
}

.wizard-status {
  color: var(--app-accent-strong);
  font-weight: 600;
}

.wizard-nav {
  display: flex;
  align-items: center;
  gap: var(--app-spacing-sm);
  margin-top: var(--app-spacing-md);
}

.wizard-slide-enter-active,
.wizard-slide-leave-active {
  transition: all 220ms ease;
}

.wizard-slide-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.wizard-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

.survey-item-card {
  border-radius: var(--app-radius-md);
  border-color: var(--app-border);
  background-color: var(--app-surface-muted);
}

.survey-item-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-sm);
  padding: var(--app-spacing-md);
}

.survey-question {
  font-weight: 600;
  color: var(--app-headline);
}

.likert-group {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-sm);
}

.likert-group :deep(.v-selection-control) {
  width: 100%;
  margin: 0;
}

.likert-group :deep(.v-input__details) {
  display: none;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--app-spacing-sm);
  margin-top: var(--app-spacing-lg);
}

.action-buttons :deep(.v-btn) {
  min-width: 220px;
  text-transform: none;
  letter-spacing: 0.08em;
  border-radius: var(--app-radius-sm);
}

.action-buttons :deep(.v-btn--variant-outlined) {
  border-color: var(--app-border);
  color: var(--app-text);
}

@media (min-width: 640px) {
  .survey-card__body {
    padding: calc(var(--app-spacing-lg) + 4px);
  }

  .survey-item-card__body {
    padding: calc(var(--app-spacing-md) + 4px);
  }

  .action-buttons {
    flex-direction: row;
    align-items: center;
  }
}

@media (min-width: 1024px) {
  .survey-container {
    padding-block: calc(var(--app-spacing-xl) + 16px);
  }
}

@media (min-width: 960px) {
  .likert-group {
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    gap: calc(var(--app-spacing-sm) + 4px);
  }

  .likert-group :deep(.v-selection-control) {
    width: auto;
    flex: 1 1 auto;
    min-width: 0;
  }
}
</style>
