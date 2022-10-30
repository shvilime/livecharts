<script setup lang="ts">
import { computed } from 'vue';
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
import ChartDataLabels from 'chartjs-plugin-datalabels';

interface InterfaceChartProperties {
  chartLegend: string
  chartLabels: string[]
  chartValues: number[]
  chartWidth: number
  chartHeight: number
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
  ChartDataLabels,
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

</script>

<template>
  <div class="chart-container">
  <Line
  chartId="line-chart"
  :width="props.chartWidth"
  :height="props.chartHeight"
  :chart-data="chartDataComputed"
  :chartOptions="props.chartOptions" />
  </div>
</template>
