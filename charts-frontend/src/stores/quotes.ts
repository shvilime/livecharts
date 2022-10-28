import { defineStore } from 'pinia';
import { InterfaceQuotes, InterfaceQuote } from 'src/interfaces';

export const useQuotesStore = defineStore('quotes', {
  state: () => ({
    tickers: [] as string[],
    selectedTicker: '',
    initializing: false,
    allPeriod: false,
    live: true,
    batchSize: 100,
    labels: [] as string[],
    values: [] as number[],
  }),
  getters: {
  },
  actions: {
    initQuotes(quotes: InterfaceQuotes) {
      this.initializing = true;
      // Очистим все котировки
      this.labels.length = 0;
      this.values.length = 0;
      // Запихнем новые котировки в хранилище
      quotes.values.forEach((element: InterfaceQuote) => {
        this.labels.push(element.created);
        this.values.push(element.value);
      });
      // Включим живые котировки, если это последняя страница
      this.live = quotes.start_live;
      this.initializing = false;
    },
    appendQuotes(quotes: InterfaceQuotes) {
      // Если тикер не выбран или идет инициализация или обновление не нужно, то сваливаем
      if (!this.selectedTicker || this.initializing || !this.live) {
        return;
      }
      // Поищем в списке цен нужное значение
      const lookup = quotes.values.find((obj) => obj.ticker === this.selectedTicker);
      if (lookup === undefined) {
        return;
      }
      // Добавим в список меток значение
      this.labels.push(lookup.created);
      this.values.push(lookup.value);
      if (this.values.length > this.batchSize) {
        this.labels.shift();
        this.values.shift();
      }
    },
  },
});
