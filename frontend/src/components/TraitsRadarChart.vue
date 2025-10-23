<template>
  <div class="chart-wrapper">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Radar } from 'vue-chartjs';
import { useDisplay } from 'vuetify';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const ACCENT_FILL = 'rgba(195, 74, 44, 0.18)';
const ACCENT_STROKE = '#c34a2c';
const ACCENT_POINT = '#9f3b22';
const GRID_COLOR = 'rgba(60, 54, 48, 0.15)';
const TICK_COLOR = 'rgba(60, 54, 48, 0.65)';
const LABEL_COLOR = '#3c3630';

const props = defineProps({
  traitScores: {
    type: Array,
    required: true
  }
});

const display = useDisplay();

const chartData = computed(() => ({
  labels: props.traitScores.map((item) => item.label),
  datasets: [
    {
      label: 'スコア',
      data: props.traitScores.map((item) => item.scaled),
      backgroundColor: ACCENT_FILL,
      borderColor: ACCENT_STROKE,
      borderWidth: 2,
      pointBackgroundColor: ACCENT_POINT,
      pointBorderColor: '#ffffff',
      pointRadius: 4,
      pointHoverRadius: 6,
      pointHoverBackgroundColor: ACCENT_STROKE,
      pointHoverBorderColor: '#ffffff'
    }
  ]
}));

const isMobile = computed(() => display.smAndDown.value);

const longestLabelLength = computed(() =>
  props.traitScores.reduce((max, item) => Math.max(max, (item.label ?? '').length), 0)
);

const horizontalPadding = computed(() => {
  if (isMobile.value) {
    return longestLabelLength.value >= 5 ? 48 : 40;
  }
  if (longestLabelLength.value >= 7) {
    return 72;
  }
  if (longestLabelLength.value >= 5) {
    return 64;
  }
  return 52;
});

const pointLabelPadding = computed(() => (isMobile.value ? 8 : 12));
const pointLabelFontSize = computed(() => (isMobile.value ? 14 : 16));

const splitPointLabel = (label) => {
  if (!label) {
    return label;
  }

  if (label === '神経症傾向') {
    return ['神経症', '傾向'];
  }

  if (label.includes(' ')) {
    return label.split(' ').filter(Boolean);
  }

  return label;
};

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: {
      top: 24,
      bottom: 24,
      left: horizontalPadding.value,
      right: horizontalPadding.value
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: true,
      callbacks: {
        title: (context) => context[0]?.label ?? '',
        label: (context) => `スコア: ${context.parsed.r ?? context.parsed}`
      },
      displayColors: false,
      backgroundColor: 'rgba(60, 54, 48, 0.92)',
      titleFont: {
        size: 14,
        weight: '600'
      },
      bodyFont: {
        size: 13
      },
      padding: 12,
      cornerRadius: 8
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      min: 0,
      max: 100,
      angleLines: {
        color: GRID_COLOR
      },
      grid: {
        color: GRID_COLOR
      },
      ticks: {
        stepSize: 20,
        color: TICK_COLOR,
        showLabelBackdrop: false
      },
      pointLabels: {
        padding: pointLabelPadding.value,
        color: LABEL_COLOR,
        callback: (label) => splitPointLabel(label),
        font: {
          size: pointLabelFontSize.value,
          lineHeight: 1.2
        }
      }
    }
  },
  animation: {
    duration: 1000,
    easing: 'easeOutQuart'
  }
}));
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: clamp(340px, 75vw, 620px);
  max-width: 620px;
  margin: 0 auto;
}

@media (min-width: 1280px) {
  .chart-wrapper {
    height: 680px;
    max-width: 680px;
  }
}
</style>
