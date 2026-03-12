import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "@/features/auth/model/authStore";
import { Search, MessageCircle, BookOpen, LayoutDashboard } from "lucide-react";

export default function Sidebar() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin";
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const menuItems = [
    { path: "/", label: "Tra Cứu Pháp Luật", icon: Search },
    { path: "/consultant", label: "AI Tư Vấn", icon: MessageCircle },
    { path: "/tracking", label: "Theo Dõi", icon: BookOpen },
  ];

  return (
    <div className="w-64 bg-slate-50 border-r border-slate-200 min-h-[calc(100vh-4rem)] p-6 flex flex-col">
      <nav className="flex-1 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`group flex items-center gap-3 px-4 py-3 rounded-lg border transition-all duration-200 ${
                active
                  ? "border-blue-500 text-blue-600 bg-white"
                  : "border-transparent text-slate-600 hover:bg-slate-200"
              }`}
            >
              <Icon
                size={20}
                className={`${
                  active
                    ? "text-blue-600"
                    : "text-slate-500 group-hover:text-slate-700"
                }`}
              />
              <span className="font-medium text-sm">{item.label}</span>
            </Link>
          );
        })}

        {/* Admin Section */}
        {isAdmin && (
          <div className="pt-4 mt-4 border-t border-slate-200">
            <Link
              to="/admin/dashboard"
              className={`group flex items-center gap-3 px-4 py-3 rounded-lg border transition-all duration-200 ${
                isActive("/admin/dashboard")
                  ? "border-blue-500 text-blue-600 bg-white"
                  : "border-transparent text-slate-600 hover:bg-slate-200"
              }`}
            >
              <LayoutDashboard
                size={20}
                className={`${
                  isActive("/admin/dashboard")
                    ? "text-blue-600"
                    : "text-slate-500 group-hover:text-slate-700"
                }`}
              />
              <span className="font-medium text-sm">Quản Lý</span>
            </Link>
          </div>
        )}
      </nav>

      {/* User Info Footer */}
      <div className="border-t border-slate-200 pt-4">
        <div className="text-xs text-slate-600 truncate">
          {user?.full_name || user?.email}
        </div>
      </div>
    </div>
  );
}
