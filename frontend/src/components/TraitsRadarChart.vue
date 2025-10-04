<template>
  <div class="chart-wrapper">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Radar } from 'vue-chartjs';
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

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      beginAtZero: true,
      min: 0,
      max: 100,
      ticks: {
        stepSize: 20
      },
      pointLabels: {
        font: {
          size: 16
        }
      }
    }
  }
}));
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  height: 480px;
}

@media (min-width: 960px) {
  .chart-wrapper {
    height: 600px;
  }
}
</style>
