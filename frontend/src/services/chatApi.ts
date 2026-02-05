import axios from "axios";
import type { ChatResponse } from "@/types";
const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

// Tự động gắn Token vào Header ---
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const login = (formData: FormData) => api.post("/auth/login", formData);
export const register = (data: any) => api.post("/auth/register", data);
export const getMe = () => api.get("/auth/me");

// Chat APIs
export const fetchSessions = () => api.get("/sessions");
export const fetchHistory = (id: number) => api.get(`/history/${id}`);
export const createSession = () => api.post("/session/start");
export const deleteSession = (id: number) => api.delete(`/session/${id}`);
export const sendMessage = (payload: { query: string; session_id: number }) =>
  api.post<ChatResponse>("/chat", payload);
