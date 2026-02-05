import { createContext, useContext, useState, useEffect } from "react";
import { getMe, login as loginApi } from "@/services/chatApi";
import type { ReactNode } from "react";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin";
}

interface AuthContextType {
  user: User | null;
  login: (formData: FormData) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getMe()
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (formData: FormData) => {
    const res = await loginApi(formData);
    localStorage.setItem("token", res.data.access_token);
    const userRes = await getMe();
    setUser(userRes.data);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
