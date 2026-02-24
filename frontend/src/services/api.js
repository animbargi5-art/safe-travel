import axios from "axios";

/**
 * Central API instance
 * - Single source of truth for backend communication
 * - Easy to switch between dev / prod later
 */

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds safety timeout
});

/**
 * Request interceptor
 * (Later: auth token, logging, etc.)
 */
api.interceptors.request.use(
  (config) => {
    // Example for future:
    // const token = localStorage.getItem("token");
    // if (token) config.headers.Authorization = `Bearer ${token}`;

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor
 * Central error handling
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Network / server errors handled consistently
    if (!error.response) {
      console.error("Network error or server not reachable");
    } else {
      console.error(
        "API Error:",
        error.response.status,
        error.response.data
      );
    }

    return Promise.reject(error);
  }
);

export default api;
