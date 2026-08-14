import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { createSession } from "./api";

function AppBootstrap() {
  useEffect(() => {
    createSession()
      .then((response) => {
        console.log("DHIRA session:", response.data);
      })
      .catch((error) => {
        console.error("DHIRA session initialization failed:", error);
      });
  }, []);

  return <App />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppBootstrap />
  </React.StrictMode>
);