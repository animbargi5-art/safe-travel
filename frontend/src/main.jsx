import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Capacitor } from '@capacitor/core';
import App from "./App";
import MobileApp from "./mobile/MobileApp";
import "./index.css";

// Use MobileApp wrapper when running in Capacitor (native mobile)
const AppComponent = Capacitor.isNativePlatform() ? MobileApp : App;

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppComponent />
    </BrowserRouter>
  </React.StrictMode>
);
