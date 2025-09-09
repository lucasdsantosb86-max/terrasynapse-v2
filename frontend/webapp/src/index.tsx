import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import TerraSynapseEnterprise from "./components/TerraSynapseEnterprise";

const root = createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <TerraSynapseEnterprise />
  </React.StrictMode>
);
