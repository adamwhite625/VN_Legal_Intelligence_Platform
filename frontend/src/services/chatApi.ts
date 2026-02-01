import axios from "axios";
import type { ChatResponse } from "@/types";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

export const fetchSessions = () => api.get("/sessions");
export const fetchHistory = (id: number) => api.get(`/history/${id}`);
export const createSession = () => api.post("/session/start");
export const deleteSession = (id: number) => api.delete(`/session/${id}`);

export const sendMessage = (payload: { query: string; session_id: number }) =>
  api.post<ChatResponse>("/chat", payload);
