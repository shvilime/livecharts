export interface InterfaceResponse {
  msg?: string | '';
  errors?: string[];
}

export interface InterfaceTickers {
  tickers: string[];
}

export interface InterfaceQuote {
  created: string;
  ticker: string;
  value: number;
}

export interface InterfaceQuotes {
  start_live: boolean
  values: InterfaceQuote[];
}
