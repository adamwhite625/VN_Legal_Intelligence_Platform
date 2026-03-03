import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "@/shared/layout/MainLayout";
import { useTrackingStore } from "@/features/search/model/trackingStore";
import { useConsultantStore } from "@/features/consultant/model/consultantStore";

export default function TrackingPage() {
  const navigate = useNavigate();
  const {
    loadSavedLaws,
    loadSavedQuestions,
    loadStats,
    savedLaws,
    savedQuestions,
    stats,
  } = useTrackingStore();

  const { sessions, loadSessions, removeSessions, loadSessionHistory } =
    useConsultantStore();

  const [activeTab, setActiveTab] = useState<
    "laws" | "questions" | "stats" | "chats"
  >("laws");
  const [loading, setLoading] = useState(true);
  const [expandedSessionId, setExpandedSessionId] = useState<number | null>(
    null,
  );

  useEffect(() => {
    setLoading(true);
    Promise.all([
      loadSavedLaws(),
      loadSavedQuestions(),
      loadStats(),
      loadSessions(),
    ]).finally(() => {
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📚 Theo Dõi Pháp Lý
          </h1>
          <p className="text-gray-600">
            Quản lý các luật, câu hỏi và session đã lưu
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b overflow-x-auto">
          <button
            onClick={() => setActiveTab("laws")}
            className={`px-4 py-2 font-medium transition whitespace-nowrap ${
              activeTab === "laws"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            📖 Luật Đã Lưu ({savedLaws.length})
          </button>
          <button
            onClick={() => setActiveTab("questions")}
            className={`px-4 py-2 font-medium transition whitespace-nowrap ${
              activeTab === "questions"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            💬 Câu Hỏi ({savedQuestions.length})
          </button>
          <button
            onClick={() => setActiveTab("chats")}
            className={`px-4 py-2 font-medium transition whitespace-nowrap ${
              activeTab === "chats"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            📋 Lịch sử Chat ({sessions.length})
          </button>
          <button
            onClick={() => setActiveTab("stats")}
            className={`px-4 py-2 font-medium transition whitespace-nowrap ${
              activeTab === "stats"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            📊 Thống Kê
          </button>
        </div>

        {/* Content */}
        {activeTab === "laws" && (
          <div className="space-y-4">
            {savedLaws.length === 0 ? (
              <div className="bg-white p-8 rounded-lg text-center text-gray-500">
                Chưa có luật nào được lưu
              </div>
            ) : (
              savedLaws.map((law) => (
                <div
                  key={law.id}
                  className="bg-white p-4 rounded-lg border hover:shadow-lg transition cursor-pointer"
                  onClick={() =>
                    navigate(`/law-detail/${law.slug || law.law_id}`)
                  }
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-lg text-gray-900">
                      {law.law_title}
                    </h3>
                    <span className="text-xs text-gray-500">
                      {new Date(law.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-2">
                    {law.law_type && (
                      <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
                        {law.law_type}
                      </span>
                    )}
                    {law.law_year && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                        {law.law_year}
                      </span>
                    )}
                    {law.law_authority && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                        {law.law_authority}
                      </span>
                    )}
                  </div>

                  {law.notes && (
                    <p className="text-sm text-gray-600 italic">
                      Ghi chú: {law.notes}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "questions" && (
          <div className="space-y-4">
            {savedQuestions.length === 0 ? (
              <div className="bg-white p-8 rounded-lg text-center text-gray-500">
                Chưa có câu hỏi nào được lưu
              </div>
            ) : (
              savedQuestions.map((q) => (
                <div
                  key={q.id}
                  className="bg-white p-4 rounded-lg border hover:shadow-lg transition"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-900 flex-1">
                      {q.question}
                    </h3>
                    <span className="text-xs text-gray-500 ml-2">
                      {new Date(q.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {q.answer && (
                    <div className="mb-2 p-2 bg-gray-50 rounded text-sm text-gray-700">
                      <strong>Trả lời:</strong> {q.answer.substring(0, 200)}...
                    </div>
                  )}

                  {q.tags && q.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {q.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={() =>
                      q.law_id && navigate(`/law-detail/${q.law_id}`)
                    }
                    className="text-xs text-blue-600 hover:underline"
                  >
                    → Xem luật liên quan
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "chats" && (
          <div className="space-y-4">
            {sessions.length === 0 ? (
              <div className="bg-white p-8 rounded-lg text-center text-gray-500">
                Chưa có phiên chat nào được lưu
              </div>
            ) : (
              sessions.map((session) => (
                <div key={session.id} className="bg-white rounded-lg border">
                  <div
                    onClick={() =>
                      setExpandedSessionId(
                        expandedSessionId === session.id ? null : session.id,
                      )
                    }
                    className="p-4 cursor-pointer hover:bg-gray-50 transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">
                          {session.title ||
                            `Chat ${new Date(session.created_at).toLocaleDateString()}`}
                        </h3>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700">
                            {session.session_type === "law-detail"
                              ? "📖 Chat về luật"
                              : "🤖 AI Consultant"}
                          </span>
                          {session.law_id && (
                            <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">
                              Luật: {session.law_id}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-xs text-gray-500 mb-1">
                          Tạo:{" "}
                          {new Date(session.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          Cập nhật:{" "}
                          {new Date(session.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  {expandedSessionId === session.id && (
                    <div className="border-t px-4 py-3 bg-gray-50 space-y-2">
                      <button
                        onClick={async () => {
                          await loadSessionHistory(session.id);
                          navigate("/consultant");
                        }}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition text-sm"
                      >
                        💬 Xem chi tiết chat
                      </button>
                      <button
                        onClick={async () => {
                          if (
                            confirm("Bạn có chắc chắn muốn xóa phiên chat này?")
                          ) {
                            await removeSessions(session.id);
                          }
                        }}
                        className="w-full bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded transition text-sm"
                      >
                        🗑️ Xóa phiên chat
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "stats" && stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600 text-sm mb-2">📖 Luật Đã Lưu</p>
              <p className="text-3xl font-bold text-blue-600">
                {stats.total_saved_laws}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600 text-sm mb-2">💬 Câu Hỏi</p>
              <p className="text-3xl font-bold text-green-600">
                {stats.total_saved_questions}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600 text-sm mb-2">💭 Session</p>
              <p className="text-3xl font-bold text-purple-600">
                {stats.total_sessions}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600 text-sm mb-2">⏰ Gần Đây</p>
              <p className="text-3xl font-bold text-orange-600">
                {stats.recent_sessions.length}
              </p>
            </div>
          </div>
        )}

        {activeTab === "stats" && stats && (
          <div className="bg-white p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Các Session Gần Đây</h3>
            <div className="space-y-2">
              {stats.recent_sessions.map((session) => (
                <div
                  key={session.id}
                  className="p-3 border rounded hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate(`/law-detail/${session.law_id}`)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">
                        {session.title || "Session"}
                      </p>
                      <p className="text-xs text-gray-500">
                        {session.session_type === "law-detail"
                          ? `📖 Về luật: ${session.law_id}`
                          : "🤖 Trao đổi tổng quát"}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
