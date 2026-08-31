import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import Stocks from "./pages/Stocks";
import StockDetail from "./pages/StockDetail";

export default function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <div className="mx-auto max-w-[1600px] px-4 pb-10 pt-4 md:px-6 xl:px-8">
          <Header />
          <main className="pt-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stocks" element={<Stocks />} />
              <Route path="/stocks/:symbol" element={<StockDetail />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
