import AppRouter from "./router";
import AppProviders from "./providers";
import { useEffect } from "react";
import { useAuthStore } from "@/features/auth/model/authStore";

export default function App() {
  const { token, fetchUser } = useAuthStore();

  useEffect(() => {
    if (token) {
      fetchUser();
    }
  }, [token]);

  return (
    <AppProviders>
      <AppRouter />
    </AppProviders>
  );
}
