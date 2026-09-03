import axios from "axios";

// Local development → FastAPI directly
// Production → Vercel proxies /api requests to Render
const API_URL = import.meta.env.DEV
  ? import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
  : "/api";

const API = axios.create({
  baseURL: API_URL,
});

const WS_URL = import.meta.env.VITE_WS_URL || (
  import.meta.env.DEV
    ? "ws://127.0.0.1:8000/ws/market"
    : "wss://smart-investor-platform-kmsq.onrender.com/ws/market"
);

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

// Automatically send the guest ID with every API request
API.interceptors.request.use((config) => {
  config.headers["X-Guest-ID"] = getGuestId();
  return config;
});

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

export const getZerodhaLoginUrl = () =>
  API.get<{ login_url: string }>("/broker/zerodha/connect");

export const fetchZerodhaStatus = () =>
  API.get<{ connected: boolean; user_id: string | null }>("/broker/zerodha/status");

export const previewZerodhaOrder = (order: {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  reference_price: number;
}) => API.post("/broker/zerodha/order/preview", order);

export const placeZerodhaOrder = (order: {
  preview_id: string;
  idempotency_key: string;
  confirmed: boolean;
}) => API.post("/broker/zerodha/order", order);

export const connectMarketStream = (
  symbols: string[],
  onMessage: (message: any) => void,
  reconnectDelayMs = 3000
) => {
  let socket: WebSocket | null = null;
  let isClosed = false;
  let reconnectTimer: number | null = null;
  let heartbeat: number | null = null;
  let connectionGeneration = 0;
  let reconnectAttempts = 0;

  const clearHeartbeat = () => {
    if (heartbeat !== null) {
      window.clearInterval(heartbeat);
      heartbeat = null;
    }
  };

  const scheduleReconnect = (generation: number) => {
    if (isClosed || generation !== connectionGeneration || reconnectTimer !== null) {
      return;
    }

    const delay = Math.min(
      reconnectDelayMs * 2 ** reconnectAttempts,
      30000,
    );
    reconnectAttempts += 1;
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, delay);
  };

  const connect = () => {
    if (isClosed) return;

    const generation = ++connectionGeneration;
    const currentSocket = new WebSocket(WS_URL);
    socket = currentSocket;

    currentSocket.addEventListener("open", () => {
      if (isClosed || generation !== connectionGeneration) {
        currentSocket.close();
        return;
      }

      reconnectAttempts = 0;
      currentSocket.send(JSON.stringify({ type: "subscribe", symbols }));

      clearHeartbeat();
      heartbeat = window.setInterval(() => {
        if (currentSocket.readyState === WebSocket.OPEN) {
          currentSocket.send(JSON.stringify({ type: "ping" }));
        }
      }, 25000);
    });

    currentSocket.addEventListener("close", () => {
      if (generation !== connectionGeneration) return;
      clearHeartbeat();
      socket = null;
      scheduleReconnect(generation);
    }, { once: true });

    currentSocket.addEventListener("error", () => {
      currentSocket.close();
    });

    currentSocket.addEventListener("message", (event) => {
      if (generation !== connectionGeneration) return;
      try {
        const message = JSON.parse(event.data);
        if (message?.type === "pong") return;
        onMessage(message);
      } catch {
        // Ignore malformed websocket payloads.
      }
    });
  };

  connect();

  return {
    close: () => {
      isClosed = true;
      connectionGeneration += 1;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      reconnectTimer = null;
      clearHeartbeat();
      socket?.close();
      socket = null;
    },
    sendSymbols: (nextSymbols: string[]) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "subscribe", symbols: nextSymbols }));
      }
    },
  };
};