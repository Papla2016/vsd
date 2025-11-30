import React from "react";
import { createRoot } from "react-dom/client";
import VsdToSqlApp from "./VsdToSqlApp";
import "./styles.css";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(
  <React.StrictMode>
    <VsdToSqlApp />
  </React.StrictMode>
);
