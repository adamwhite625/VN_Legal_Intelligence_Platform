import { create } from "zustand";
import { getCurrentUser } from "../api/authApi";

interface User {
  email: string;
  full_name?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => Promise<void>;
  fetchUser: () => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("token"),
  user: null,

  setToken: async (token) => {
    localStorage.setItem("token", token);
    set({ token });
    await useAuthStore.getState().fetchUser();
  },

  fetchUser: async () => {
    try {
      const user = await getCurrentUser();
      set({ user });
    } catch {
      set({ user: null });
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    set({ token: null, user: null });
  },
}));
