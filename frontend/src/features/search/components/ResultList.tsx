import { useSearchStore } from "../model/searchStore";
import { useTrackingStore } from "../model/trackingStore";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { saveLawAndCreateSession } from "../api/searchApi";

export default function ResultList() {
  const { results, keyword, loading } = useSearchStore();
  const { saveLaw } = useTrackingStore();
  const navigate = useNavigate();
  const [savingId, setSavingId] = useState<string | null>(null);
  const [savedLaws, setSavedLaws] = useState<Set<string>>(new Set());

  const handleSaveLaw = async (e: React.MouseEvent, law: any) => {
    e.preventDefault();
    e.stopPropagation();

    setSavingId(law.id);
    try {
      // Save law first
      await saveLaw(
        law.id,
        law.title,
        law.type,
        law.year,
        law.authority,
        law.content,
      );
      setSavedLaws((prev) => new Set([...prev, law.id]));

      // Then create session and navigate
      const result = await saveLawAndCreateSession(law.id);
      // Use slug for URL if available, otherwise fall back to law.id
      const lawPath = result.slug || law.id;
      navigate(`/law-detail/${lawPath}`, {
        state: { sessionId: result.session_id },
      });
    } catch (error) {
      console.error("Failed to save law:", error);
      alert("Lỗi khi lưu luật. Vui lòng thử lại!");
    } finally {
      setSavingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
      </div>
    );
  }

  if (!keyword.trim()) {
    return null; // Show BrowseCategories instead
  }

  if (results.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl shadow text-center">
        <div className="text-4xl mb-3">🔍</div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Không tìm thấy kết quả
        </h3>
        <p className="text-gray-600 mb-4">
          Không tìm thấy kết quả cho "<strong>{keyword}</strong>"
        </p>
        <p className="text-sm text-gray-500">
          Hãy thử tìm kiếm với từ khóa khác hoặc duyệt theo danh mục bên dưới
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-sm text-gray-600 mb-4">
        Tìm thấy <strong>{results.length}</strong> kết quả
      </div>
      {results.map((law) => (
        <div key={law.id} className="flex gap-3 items-start">
          <Link to={`/law/${law.id}?keyword=${keyword}`} className="flex-1">
            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition cursor-pointer border border-gray-100 hover:border-blue-400">
              <div className="mb-2">
                {law.id && (
                  <div className="inline-block bg-blue-600 text-white px-3 py-1.5 rounded text-sm font-semibold">
                    {law.id}
                  </div>
                )}
              </div>

              <h3 className="font-bold text-gray-900 text-lg leading-snug mb-2 line-clamp-2">
                {law.title}
              </h3>

              <div className="flex flex-wrap gap-2 mb-3">
                {law.year && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-gray-100 text-gray-700 font-medium">
                    📅 {law.year}
                  </span>
                )}
                {law.authority && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-green-50 text-green-700 font-medium">
                    🏛️ {law.authority}
                  </span>
                )}
                {law.type && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-orange-50 text-orange-700 font-medium">
                    📄 {law.type}
                  </span>
                )}
              </div>

              <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                {law.description || law.content?.substring(0, 150)}
              </p>

              <div className="mt-3 flex items-center text-blue-600 text-sm font-medium group">
                <span>Xem chi tiết</span>
                <span className="ml-1 group-hover:translate-x-1 transition">
                  →
                </span>
              </div>
            </div>
          </Link>

          <button
            onClick={(e) => handleSaveLaw(e, law)}
            disabled={savingId === law.id}
            className={`px-3 py-3 rounded-lg h-fit font-bold text-lg transition whitespace-nowrap ${
              savedLaws.has(law.id || "")
                ? "bg-yellow-100 text-yellow-600 hover:bg-yellow-200"
                : "bg-blue-100 text-blue-600 hover:bg-blue-200"
            } ${savingId === law.id ? "opacity-50 cursor-not-allowed" : ""}`}
            title={
              savedLaws.has(law.id || "")
                ? "Đã lưu - Click để chat về luật này"
                : "Lưu và chat về luật này"
            }
          >
            {savingId === law.id ? (
              <span className="inline-block animate-spin">⏳</span>
            ) : savedLaws.has(law.id || "") ? (
              "✓"
            ) : (
              "💾"
            )}
          </button>
        </div>
      ))}
    </div>
  );
}
