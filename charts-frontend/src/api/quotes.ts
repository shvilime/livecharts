import { api } from 'api/index';
import moment from 'moment';
import { InterfaceQuotes, InterfaceTickers } from 'interfaces/index';

export async function apiGetTickers(): Promise<InterfaceTickers> {
  const json = await api.get('/api/quotes/tickers').json();
  return json as Promise<InterfaceTickers>;
}

export async function apiGetPrices(
  ticker: string,
  back: boolean,
  startDate: Date,
  limit = 100,
): Promise<InterfaceQuotes> {
  const json = await api.get(
    `/api/quotes/history/${ticker}`,
    {
      searchParams: {
        back,
        start: moment(startDate).format('YYYY-MM-DDTHH:mm:ss'),
        limit,
      },
    },
  ).json();

  return json as Promise<InterfaceQuotes>;
}
