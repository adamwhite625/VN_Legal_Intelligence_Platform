import axios from "axios";

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin";
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_sessions: number;
  total_messages: number;
  recent_users: User[];
}

// ============================================================================
// API Client
// ============================================================================

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// API Methods
// ============================================================================

export async function getAdminStats(): Promise<AdminStats> {
  const response = await api.get("/admin/stats");
  return response.data;
}

export async function getAllUsers(
  skip: number = 0,
  limit: number = 50,
): Promise<User[]> {
  const response = await api.get("/admin/users", {
    params: { skip, limit },
  });
  return response.data;
}

// ============================================================================
// Admin API Object
// ============================================================================

export const adminApi = {
  getStats: getAdminStats,
  getAllUsers: getAllUsers,
};

export default api;
