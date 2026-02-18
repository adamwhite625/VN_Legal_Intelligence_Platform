import { useState, useEffect } from "react";
import { getLawDetail, type LawItem } from "@/features/search/api/searchApi";

interface Props {
  open: boolean;
  lawId: string;
  onClose: () => void;
}

export default function LawDetailPanel({ open, lawId, onClose }: Props) {
  const [law, setLaw] = useState<LawItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!open || !lawId) return;

    setLoading(true);
    setError("");

    // 🧹 FORCE: Always fetch from raw_law_data.json, NOT VectorDB
    getLawDetail(lawId, "json")
      .then((data) => {
        setLaw(data);
      })
      .catch((err) => {
        console.error("Error fetching law detail:", err);
        setError("Không thể tải thông tin chi tiết");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [open, lawId]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-5 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">📋 Chi tiết Luật</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition text-gray-500 hover:text-gray-700"
            title="Đóng"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto flex-1 p-6">
          {loading ? (
            <div className="flex justify-center items-center py-16">
              <div className="animate-spin rounded-full h-10 w-10 border-3 border-gray-300 border-t-blue-600"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          ) : law ? (
            <div className="space-y-5">
              {/* Title Section */}
              <div className="pb-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-3">
                  {law.title}
                </h3>

                {/* Metadata Badges */}
                <div className="flex flex-wrap gap-2">
                  {law.id && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
                      📌 {law.id}
                    </span>
                  )}
                  {law.year && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                      📅 {law.year}
                    </span>
                  )}
                  {law.authority && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-200">
                      🏛️ {law.authority}
                    </span>
                  )}
                  {law.type && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-medium border border-purple-200">
                      📋 {law.type}
                    </span>
                  )}
                </div>
              </div>

              {/* Description */}
              {law.description && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    📝 Tóm tắt
                  </h4>
                  <p className="text-gray-700 leading-relaxed italic border-l-4 border-blue-300 pl-3">
                    {law.description}
                  </p>
                </div>
              )}

              {/* Content */}
              {law.content && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    📄 Nội dung
                  </h4>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="text-sm text-gray-800 whitespace-pre-wrap break-words leading-relaxed max-h-64 overflow-y-auto">
                      {law.content.substring(0, 2500)}
                      {law.content.length > 2500 && (
                        <p className="text-xs text-gray-500 mt-3 italic">
                          ↓ Nội dung được cắt ngắn (xem đầy đủ trong trang chi
                          tiết)
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Không có dữ liệu
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
