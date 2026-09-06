import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { createSession } from "./api";

function AppBootstrap() {
  const [isReady, setIsReady] = React.useState(false);

  useEffect(() => {
    createSession()
      .then((response) => {
        console.log("DHIRA session:", response.data);
        setIsReady(true);
      })
      .catch((error) => {
        console.error("DHIRA session initialization failed:", error);
        setIsReady(true); // Still render even if it fails, maybe gracefully degrade
      });
  }, []);

  if (!isReady) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Initializing DHIRA Session...</div>;
  }

  return <App />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppBootstrap />
  </React.StrictMode>
);