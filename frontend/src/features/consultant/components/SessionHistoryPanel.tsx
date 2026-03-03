import { useEffect, useState } from "react";
import { useConsultantStore } from "../model/consultantStore";

interface Props {
  onSelectSession?: (sessionId: number) => void;
}

export default function SessionHistoryPanel({ onSelectSession }: Props) {
  const { sessions, loadSessions, removeSessions, currentSessionId } =
    useConsultantStore();
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    loadSessions().finally(() => setLoading(false));
  }, [loadSessions]);

  const handleSelectSession = (sessionId: number) => {
    if (onSelectSession) {
      onSelectSession(sessionId);
    }
  };

  const handleDeleteSession = async (
    sessionId: number,
    e: React.MouseEvent,
  ) => {
    e.stopPropagation();
    if (!confirm("Bạn có chắc chắn muốn xóa phiên chat này?")) return;

    setDeletingId(sessionId);
    try {
      await removeSessions(sessionId);
    } finally {
      setDeletingId(null);
    }
  };

  const getSessionTypeLabel = (type: string) => {
    return type === "law-detail" ? "📖 Chat về luật" : "🤖 Consultant";
  };

  const getSessionTypeColor = (type: string) => {
    return type === "law-detail"
      ? "border-green-200 bg-green-50"
      : "border-blue-200 bg-blue-50";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Hôm qua";
    } else {
      return date.toLocaleDateString("vi-VN");
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow p-4 h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col h-full">
      <div className="mb-4">
        <h3 className="font-semibold text-lg mb-2">📋 Lịch sử chat</h3>
        <p className="text-xs text-gray-500">{sessions.length} phiên chat</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {sessions.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-8">
            Chưa có phiên chat nào
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => handleSelectSession(session.id)}
              className={`p-3 rounded-lg border-2 cursor-pointer transition ${
                currentSessionId === session.id
                  ? "border-blue-500 bg-blue-50"
                  : `${getSessionTypeColor(session.session_type)} hover:border-blue-300`
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {session.title ||
                        `Chat ${formatDate(session.created_at)}`}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600 whitespace-nowrap">
                      {getSessionTypeLabel(session.session_type)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {formatDate(session.created_at)}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  disabled={deletingId === session.id}
                  className="flex-shrink-0 text-gray-400 hover:text-red-500 transition disabled:opacity-50"
                  title="Xóa phiên chat"
                >
                  {deletingId === session.id ? (
                    <span className="inline-block animate-spin">⌛</span>
                  ) : (
                    "✕"
                  )}
                </button>
              </div>

              {session.law_id && (
                <p className="text-xs text-gray-600 mt-2">
                  Luật: <span className="font-medium">{session.law_id}</span>
                </p>
              )}
            </div>
          ))
        )}
      </div>

      <button
        onClick={() => loadSessions()}
        className="mt-4 w-full text-sm text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded transition"
      >
        🔄 Làm mới
      </button>
    </div>
  );
}
