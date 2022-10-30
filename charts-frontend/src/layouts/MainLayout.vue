<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar class="q-py-sm q-px-md">
        <q-toolbar-title>
          <q-avatar text-color="primary" color="white" icon="query_stats"></q-avatar>
          Live Charts
        </q-toolbar-title>
        <q-toggle
          v-if="quotesStore.selectedTicker"
          v-model="quotesStore.allPeriod"
          class="q-pr-sm"
          color="yellow"
          checked-icon="check"
          unchecked-icon="clear"
          label="Весь период"
          @update:model-value="onChangeLoadTicker"/>
        <q-select
          v-model="quotesStore.selectedTicker"
          square
          dense
          standout="bg-primary text-white"
          label-color="white"
          :options="quotesStore.tickers"
          :stack-label="false"
          label="Выберите график .."
          style="width: 200px"
          @update:model-value="onChangeLoadTicker"/>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useQuotesStore } from 'stores/quotes';
import { apiGetTickers, apiGetPrices } from 'api/quotes';
import { InterfaceTickers, InterfaceQuotes } from 'src/interfaces';

const $q = useQuasar();
const quotesStore = useQuotesStore();

async function loadTickers() {
  // Получим с бэка список тикеров и в хранилище
  try {
    const { tickers } = await apiGetTickers() as InterfaceTickers;
    quotesStore.tickers = tickers;
  } catch (e) {
    $q.notify({
      type: 'negative',
      message: 'Ошибка получения списка тикеров с сервера',
    });
    console.warn((e as Error).message);
  }
}

async function onChangeLoadTicker() {
  try {
    // получим с бэка пачку исторических котировок для заполнения начальных данных
    const quotes = await apiGetPrices(
      quotesStore.selectedTicker,
      true,
      new Date(),
      quotesStore.allPeriod ? 0 : quotesStore.batchSize,
    ) as InterfaceQuotes;
    // Запихнем их в хранилище
    quotesStore.initQuotes(quotes);
  } catch (e) {
    $q.notify({
      type: 'negative',
      message: 'Ошибка получения котировок с сервера',
    });
    console.warn((e as Error).message);
  }
}

onMounted(() => {
  loadTickers();
});

</script>
