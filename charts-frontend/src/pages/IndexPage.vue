<template>
  <q-page class="row">
      <div class="col-12">
        <q-toggle
          v-model="quotesStore.allPeriod"
          label="Весь период"
          />
        <LineChart
        :chart-legend="'Price'"
        :chart-labels="quotesStore.labels"
        :chart-values="quotesStore.values"
        :chart-options="chartOptions"/>
        <q-btn
          v-if="quotesStore.selectedTicker && !quotesStore.allPeriod"
          round
          dense
          color="brown-1"
          icon="keyboard_arrow_left"
          class="float-left"
          @click="getHistoryBack"/>
        <q-btn
          v-if="quotesStore.selectedTicker && !quotesStore.allPeriod"
          round
          dense
          color="brown-1"
          icon="keyboard_arrow_right"
          class="float-right"
          @click="getHistoryForward"/>
      </div>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { apiGetPrices } from 'api/quotes';
import { useQuotesStore } from 'stores/quotes';
import { InterfaceQuotes } from 'src/interfaces';
import LineChart from 'components/LineChart.vue';

const $q = useQuasar();
// Инициализируем хранилище
const quotesStore = useQuotesStore();

// Параметры графика
const chartOptions = {
  scales: {
    x: {
      ticks: {
        display: !quotesStore.allPeriod,
      },
    },
  },
  elements: { point: { radius: 1 }, line: { borderWidth: 2 } },
};

async function getHistoryBack() {
  // Получим из хранилища дату первой доступной котировки
  const firstDateLabel = quotesStore.labels.slice(0, 1).pop();
  try {
    // получим с бэка пачку предыдущих исторических котировок
    const quotes = await apiGetPrices(
      quotesStore.selectedTicker,
      true,
      new Date(firstDateLabel as string),
      quotesStore.batchSize,
    ) as InterfaceQuotes;
    // Запихнем их в хранилище
    quotesStore.initQuotes(quotes);
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Ошибка получения котировок с сервера' });
    console.warn((e as Error).message);
  }
}

async function getHistoryForward() {
  // Получим из хранилища дату последней доступной котировки
  const lastDateLabel = quotesStore.labels.slice(-1).pop();
  try {
    // получим с бэка пачку следующих исторических котировок
    const quotes = await apiGetPrices(
      quotesStore.selectedTicker,
      false,
      new Date(lastDateLabel as string),
      quotesStore.batchSize,
    ) as InterfaceQuotes;
    // Запихнем их в хранилище
    quotesStore.initQuotes(quotes);
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Ошибка получения котировок с сервера' });
    console.warn((e as Error).message);
  }
}

</script>
