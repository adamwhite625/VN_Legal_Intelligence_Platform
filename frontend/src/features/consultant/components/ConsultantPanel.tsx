import { useState, useEffect } from "react";
import { useConsultantStore } from "../model/consultantStore";
import { useTrackingStore } from "@/features/search/model/trackingStore";
import { useAuthStore } from "@/features/auth/model/authStore";
import { Link } from "react-router-dom";
import LawDetailPanel from "./LawDetailPanel";

interface Props {
  context: string;
  contextType?: "general" | "law-detail";
  lawId?: string;
}

export default function ConsultantPanel({
  context,
  contextType = "general",
  lawId,
}: Props) {
  const { token } = useAuthStore();
  const { messages, sendMessage, loading, initSession } = useConsultantStore();
  const { saveQuestion } = useTrackingStore();

  const [input, setInput] = useState("");
  const [selectedLawId, setSelectedLawId] = useState<string>("");
  const [showLawDetail, setShowLawDetail] = useState(false);
  const [savingQuestion, setSavingQuestion] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [questionNotes, setQuestionNotes] = useState("");

  // Init session when component mounts
  useEffect(() => {
    initSession(contextType, lawId);
  }, [contextType, lawId, initSession]);

  const handleSend = async () => {
    if (!input.trim()) return;

    await sendMessage(input, context, lawId);
    setInput("");
  };

  const handleSaveQuestion = async () => {
    if (!input.trim()) return;

    setSavingQuestion(true);
    try {
      const lastMsg = messages[messages.length - 1];
      const answer = lastMsg?.sender === "assistant" ? lastMsg.text : undefined;

      await saveQuestion(
        input,
        answer,
        contextType === "law-detail" ? lawId : undefined,
        questionNotes
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      );

      setShowSaveDialog(false);
      setQuestionNotes("");
      alert("Câu hỏi đã được lưu!");
    } catch (error) {
      console.error("Failed to save question:", error);
      alert("Lỗi khi lưu câu hỏi!");
    } finally {
      setSavingQuestion(false);
    }
  };

  const handleSourceClick = (source: string) => {
    const lawIdMatch = source.match(/Điều\s+(\d+)/);
    const id = lawIdMatch ? `Điều ${lawIdMatch[1]}` : source;
    setSelectedLawId(id.trim());
    setShowLawDetail(true);
  };

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
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-semibold">
            {contextType === "law-detail"
              ? "💬 Chat về luật"
              : "🤖 AI Consultant"}
          </h2>
          <p className="text-xs text-gray-500">
            {contextType === "law-detail"
              ? "Chat với ngữ cảnh luật này"
              : "Hỏi về luật một cách tổng quát"}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4 border rounded p-3 bg-gray-50">
        {messages.length === 0 ? (
          <p className="text-center text-gray-400 text-sm py-8">
            Chưa có tin nhắn. Hãy bắt đầu hỏi!
          </p>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className="space-y-1">
              <div
                className={`p-2 rounded text-sm ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white rounded-br-none"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>

              {msg.sender === "assistant" &&
                msg.sources &&
                msg.sources.length > 0 && (
                  <div className="ml-2 p-2 bg-yellow-50 rounded text-xs border-l-2 border-yellow-300">
                    <p className="font-semibold text-gray-600 mb-1">
                      📚 Căn cứ pháp lý:
                    </p>
                    <ul className="space-y-1">
                      {msg.sources.map((source, idx) => (
                        <li
                          key={idx}
                          onClick={() => handleSourceClick(source)}
                          className="text-blue-600 cursor-pointer hover:underline list-disc list-inside"
                        >
                          {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="inline-block animate-spin">⌛</span>
            Đang xử lý...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !loading && handleSend()}
            className="flex-1 p-2 border rounded text-sm"
            placeholder={
              contextType === "law-detail"
                ? "Hỏi về luật này..."
                : "Hỏi về luật..."
            }
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition"
          >
            Gửi
          </button>
        </div>

        {/* Save question button */}
        {messages.some((m) => m.sender === "assistant") && (
          <button
            onClick={() => setShowSaveDialog(true)}
            className="w-full text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition"
          >
            💾 Lưu câu hỏi
          </button>
        )}
      </div>

      {/* Save Question Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="font-semibold mb-4">Lưu câu hỏi</h3>
            <div className="space-y-3 mb-4">
              <div>
                <label className="text-sm font-medium block mb-1">
                  Câu hỏi
                </label>
                <p className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                  {input}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">
                  Tags (cách nhau bằng dấu phẩy)
                </label>
                <input
                  type="text"
                  value={questionNotes}
                  onChange={(e) => setQuestionNotes(e.target.value)}
                  placeholder="VD: hợp đồng, lương"
                  className="w-full p-2 border rounded text-sm"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 px-4 py-2 text-sm border rounded hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={handleSaveQuestion}
                disabled={savingQuestion}
                className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {savingQuestion ? "Đang lưu..." : "Lưu"}
              </button>
            </div>
          </div>
        </div>
      )}

      <LawDetailPanel
        open={showLawDetail}
        lawId={selectedLawId}
        onClose={() => setShowLawDetail(false)}
      />
    </div>
  );
}
