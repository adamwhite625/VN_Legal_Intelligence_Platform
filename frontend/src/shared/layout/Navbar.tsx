import { useAuthStore } from "@/features/auth/model/authStore";
import { Link } from "react-router-dom";
import { LogOut } from "lucide-react";

export default function Navbar() {
  const { user, logout, token } = useAuthStore();

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-16 bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg flex items-center px-12 justify-between">
      <div className="flex items-center gap-4">
        <img
          src="/vn-emblem.jpg"
          alt="VN Emblem"
          className="h-11 w-11 rounded-full border-2 border-white shadow-md"
        />
        <h1 className="text-base font-bold text-white">Viet Nam Legal AI</h1>
      </div>

      <div className="flex items-center gap-6">
        {token && user ? (
          <>
            <span className="text-sm text-white font-medium">
              Chào, {user.full_name || user.email}
            </span>

            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 bg-white text-red-500 border-2 border-red-500 rounded-lg hover:bg-red-50 transition-colors duration-200 text-sm font-medium"
            >
              <LogOut size={18} />
              Đăng Xuất
            </button>
          </>
        ) : (
          <Link
            to="/login"
            className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors duration-200 text-sm font-medium"
          >
            Đăng Nhập
          </Link>
        )}
      </div>
    </div>
  );
}
