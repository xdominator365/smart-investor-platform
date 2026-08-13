import axios from "axios";

// Support both local development and cloud production
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const API = axios.create({
  baseURL: API_URL,
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

export const fetchMarketStatusAPI = () =>
  API.get("/market/status");

export const fetchAutoTradeDecisions = (symbol: string) =>
  API.get(`/auto-trade/decisions/${symbol}`);

export const fetchNewsInsights = (symbol: string) =>
  API.get(`/news/insights/${symbol}`);                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
