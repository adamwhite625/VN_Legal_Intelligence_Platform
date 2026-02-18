import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 bg-white shadow min-h-[calc(100vh-4rem)] p-4">
      <nav className="space-y-3">
        <Link to="/" className="block p-2 rounded hover:bg-blue-100">
          🔎 Legal Search
        </Link>

        <Link to="/consultant" className="block p-2 rounded hover:bg-blue-100">
          🤖 AI Consultant
        </Link>

        <Link to="/tracking" className="block p-2 rounded hover:bg-blue-100">
          📚 Theo Dõi Pháp Lý
        </Link>
      </nav>
    </div>
  );
}
