<script setup lang="ts">
import { computed, watch } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
} from 'chart.js';
import type { ChartOptions, ChartData } from 'chart.js';

interface InterfaceChartProperties {
  chartLegend: string
  chartLabels: string[]
  chartValues: number[]
  chartOptions: ChartOptions
}

const props = defineProps<InterfaceChartProperties>();

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
);

const chartDataComputed = computed<ChartData>((): ChartData => ({
  labels: props.chartLabels.slice(0),
  datasets: [
    {
      label: props.chartLegend,
      backgroundColor: '#f87979',
      tension: 0.5,
      data: props.chartValues.slice(0),
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

const chartOptionComputed = computed<ChartOptions>((): ChartOptions => (
  { ...chartOptions, ...props.chartOptions }
));

</script>

<template>
  <div class="chart-container">
  <Line
  chartId="line-chart"
  :width="800"
  :height="600"
  :chart-data="chartDataComputed"
  :chartOptions="chartOptionComputed" />
  </div>
</template>
