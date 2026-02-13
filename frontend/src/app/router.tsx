import { BrowserRouter, Routes, Route } from "react-router-dom";
import SearchPage from "@/features/search/pages/SearchPage";
import LawDetailPage from "@/features/law-detail/pages/LawDetailPage";
import LoginPage from "@/features/auth/pages/LoginPage";
import RegisterPage from "@/features/auth/pages/RegisterPage";
import GlobalConsultantPage from "@/features/consultant/pages/GlobalConsultantPage";

function NotFound() {
  return <div className="p-10">404 - Page Not Found</div>;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/law/:id" element={<LawDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/consultant" element={<GlobalConsultantPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
