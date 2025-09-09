import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import TerraSynapseEnterprise from "./components/TerraSynapseEnterprise";

const el = document.getElementById("root");
if (el) {
  const root = createRoot(el);
  root.render(
    <React.StrictMode>
      <TerraSynapseEnterprise />
    </React.StrictMode>
  );
}
