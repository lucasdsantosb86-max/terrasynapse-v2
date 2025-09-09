import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

// (opcional) veja se a URL do backend chegou
// console.log("API:", process.env.REACT_APP_API_URL);

const el = document.getElementById("root");
if (el) {
  const root = createRoot(el);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  // fallback raro se o root não existir
  document.body.innerHTML = "<p>Elemento #root não encontrado.</p>";
}
