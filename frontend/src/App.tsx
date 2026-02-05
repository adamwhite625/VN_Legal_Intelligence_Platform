import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";

// Import các trang
import ChatPage from "@/pages/ChatPage";
import Login from "@/pages/Login";
import Register from "@/pages/Register";

// --- COMPONENT BẢO VỆ (Cái cổng gác) ---
// Nhiệm vụ: Kiểm tra xem user có được phép vào trong không
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  // 1. Đang tải (đang check token) -> Hiện vòng quay loading
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // 2. Không có user -> Đá về trang Login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // 3. Có user -> Cho phép hiển thị nội dung bên trong (ChatPage)
  return <>{children}</>;
}

// --- APP CHÍNH ---
function App() {
  return (
    // Lớp 1: Cung cấp Auth Context cho toàn app
    <AuthProvider>
      {/* Lớp 2: Router để quản lý đường dẫn */}
      <Router>
        <Routes>
          {/* Route công khai (Ai cũng vào được) */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Route bảo mật (Phải đăng nhập mới vào được) */}
          <Route
            path="/"
            element={
              // Lớp 3: Bọc ChatPage bằng ProtectedRoute
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />

          {/* Nếu gõ đường dẫn linh tinh -> Về trang chủ */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
