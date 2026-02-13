import { useState } from "react";
import { useConsultantStore } from "../model/consultantStore";
import { useAuthStore } from "@/features/auth/model/authStore";
import { Link } from "react-router-dom";
import { useEffect } from "react";
import { useParams } from "react-router-dom";

interface Props {
  context: string;
}

export default function ConsultantPanel({ context }: Props) {
  const { token } = useAuthStore();

  const { id } = useParams();

  const [input, setInput] = useState("");
  const { messages, sendMessage, loading } = useConsultantStore();

  const handleSend = async () => {
    if (!input.trim()) return;

    await await sendMessage(input, context, id || "global");

    setInput("");
  };

  useEffect(() => {
    useConsultantStore.getState().resetMessages();
  }, [id]);

  if (!token) {
    return (
      <div className="bg-white rounded-xl shadow p-4 h-full flex flex-col justify-center items-center">
        <p className="mb-4 text-center">
          Bạn cần đăng nhập để sử dụng AI Consultant
        </p>
        <Link to="/login" className="bg-blue-600 text-white px-4 py-2 rounded">
          Đăng nhập
        </Link>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col h-full">
      <h2 className="font-semibold mb-4">AI Consultant</h2>

      <div className="flex-1 overflow-y-auto space-y-2 mb-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-2 rounded ${
              msg.sender === "user" ? "bg-blue-100" : "bg-gray-100"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border rounded"
          placeholder="Hỏi AI về luật này..."
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-blue-600 text-white px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Đang xử lý..." : "Gửi"}
        </button>
      </div>
    </div>
  );
}
