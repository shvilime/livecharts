<template>
  <q-page class="row">
      <div class="col-12">
        <LineChart
        :chart-legend="'Price'"
        :chart-labels="quotesStore.labels"
        :chart-values="quotesStore.values"
        :chart-width=$q.screen.width
        :chart-height=$q.screen.height-100
        :chart-options="chartOptions"/>
      </div>

      <!-- Кнопка показа диалога листания графика -->
      <q-page-sticky
        v-if="quotesStore.selectedTicker && !quotesStore.allPeriod"
        position="top-right"
        :offset="[18, 18]">
        <q-btn fab icon="add" color="accent" @click="showDialogSlide = !showDialogSlide" />
      </q-page-sticky>

      <!-- Диалог для графика графика -->
      <q-dialog v-model="showDialogSlide" position="right">
        <q-card style="width: 350px">
          <q-card-section class="row items-center no-wrap">
            <div>
              <div class="text-grey-bold">Slide graph</div>
            </div>

            <q-space />

            <q-btn
              flat
              round
              icon="fast_rewind"
              @click="getHistoryBack"/>
            <q-btn
              flat
              round
              icon="fast_forward"
              @click="getHistoryForward"/>
          </q-card-section>
        </q-card>
      </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
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
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: {
        display: !quotesStore.allPeriod,
      },
    },
  },
  elements: { point: { radius: 2 }, line: { borderWidth: 2 } },
};
// Параметр, показывать ли диалог листания графика
const showDialogSlide = ref(false);

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
