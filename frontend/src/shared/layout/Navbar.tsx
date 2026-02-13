import { useAuthStore } from "@/features/auth/model/authStore";
import { Link } from "react-router-dom";

export default function Navbar() {
  const { user, logout, token } = useAuthStore();

  return (
    <div className="h-16 bg-white shadow flex items-center px-6 justify-between">
      <h1 className="text-xl font-bold text-blue-600">VN Legal AI</h1>

      <div className="flex items-center gap-4">
        {token && user ? (
          <>
            <span className="text-sm text-gray-700">
              Xin chào, {user.full_name || user.email}
            </span>

            <button
              onClick={logout}
              className="text-sm text-red-500 hover:underline"
            >
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" className="text-sm text-blue-600 hover:underline">
            Đăng nhập
          </Link>
        )}
      </div>
    </div>
  );
}
