import { boot } from 'quasar/wrappers';
import { InterfaceQuotes } from 'src/interfaces';
import { useQuotesStore } from 'stores/quotes';

export default boot(() => {
  // Инициализируем хранилище
  const quotesStore = useQuotesStore();

  // Откроем подключение к сокет серверу
  const socket = new WebSocket('ws://127.0.0.1:8000/websocket/open');

  socket.addEventListener('open', () => {
    socket.send('Hello Server!');
    console.log('Succesfuly connected to scanestas server');
  });

  socket.addEventListener('message', (event) => {
    // Запихнем данные в хранилище
    const data: InterfaceQuotes = JSON.parse(event.data);
    quotesStore.appendQuotes(data);
    console.log('Message from server ', data);
  });
});
