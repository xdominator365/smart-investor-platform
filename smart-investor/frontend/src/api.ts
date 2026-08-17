import axios from "axios";

// Local development → FastAPI directly
// Production → Vercel proxies /api requests to Render
const API_URL = import.meta.env.DEV
  ? import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
  : "/api";

const API = axios.create({
  baseURL: API_URL,
});

const GUEST_ID_KEY = "dhira_guest_id";

export const getGuestId = (): string => {
  const existingGuestId = localStorage.getItem(GUEST_ID_KEY);

  if (existingGuestId) {
    return existingGuestId;
  }

  const newGuestId = crypto.randomUUID();

  localStorage.setItem(GUEST_ID_KEY, newGuestId);

  return newGuestId;
};

export const createSession = () => {
  const guestId = getGuestId();

  return API.post("/session", {
    guest_id: guestId,
  });
};

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
