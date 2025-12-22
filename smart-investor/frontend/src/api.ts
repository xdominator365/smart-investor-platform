import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const fetchStock = (symbol: string) =>
  API.get(`/stock/${symbol}`);

export const fetchSignal = (symbol: string) =>
  API.get(`/signal/${symbol}`);

export const fetchChartData = (symbol: string) =>
  API.get(`/chart/${symbol}`);

export const paperBuy = (symbol: string, quantity: number) =>
  API.post(`/paper-trade/buy`, null, {
    params: { symbol, quantity }
  });

export const paperSell = (symbol: string, quantity: number) =>
  API.post(`/paper-trade/sell`, null, {
    params: { symbol, quantity }
  });

export const paperAutoTrade = (symbol: string) =>
  API.post(`/paper-trade/auto/${symbol}`);

export const fetchPortfolio = () =>
  API.get(`/paper-trade/portfolio`);
