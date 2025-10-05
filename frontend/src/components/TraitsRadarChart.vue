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
      backgroundColor: 'rgba(33, 150, 243, 0.22)',
      borderColor: '#0d47a1',
      borderWidth: 2,
      pointBackgroundColor: '#0d47a1',
      pointBorderColor: '#fff'
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
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      min: 0,
      max: 100,
      ticks: {
        stepSize: 20
      },
      pointLabels: {
        padding: pointLabelPadding.value,
        callback: (label) => splitPointLabel(label),
        font: {
          size: pointLabelFontSize.value,
          lineHeight: 1.2
        }
      }
    }
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
