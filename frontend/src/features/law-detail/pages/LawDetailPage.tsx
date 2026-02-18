import { useParams } from "react-router-dom";
import MainLayout from "@/shared/layout/MainLayout";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import ConsultantPanel from "@/features/consultant/components/ConsultantPanel";
import { useState, useEffect } from "react";
import {
  getLawDetail,
  type LawItem,
  getQuestionsForLaw,
  type SavedQuestion,
} from "@/features/search/api/searchApi";

export default function LawDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [law, setLaw] = useState<LawItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [questions, setQuestions] = useState<SavedQuestion[]>([]);

  useEffect(() => {
    if (!id) return;

    setLoading(true);
    setError("");

    getLawDetail(id, "json")
      .then((data) => {
        setLaw(data);
      })
      .catch((err) => {
        console.error("Error fetching law:", err);
        setError("Không thể tải chi tiết văn bản");
      })
      .finally(() => {
        setLoading(false);
      });

    // Load questions for this law
    if (id) {
      getQuestionsForLaw(id)
        .then((data) => {
          setQuestions(data);
        })
        .catch((err) => {
          console.error("Error loading questions:", err);
        });
    }
  }, [id]);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="p-6 bg-red-50 text-red-700 rounded">
          {error}
          <Link to="/" className="block mt-4 text-blue-600 hover:underline">
            ← Quay lại trang chủ
          </Link>
        </div>
      </MainLayout>
    );
  }

  if (!law) {
    return (
      <MainLayout>
        <div className="p-6">
          Không tìm thấy văn bản
          <Link to="/" className="block mt-4 text-blue-600 hover:underline">
            ← Quay lại trang chủ
          </Link>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="grid grid-cols-3 gap-6 h-[calc(100vh-6rem)]">
        {/* Law Detail - Left Column */}
        <div className="col-span-2 overflow-y-auto pr-2">
          <div className="bg-white rounded-xl shadow divide-y">
            {/* Header Section */}
            <div className="p-6 space-y-4">
              <button
                onClick={() => navigate(-1)}
                className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-2"
              >
                ← Quay lại
              </button>

              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-3">
                  {law.title}
                </h1>

                {/* Metadata Badges */}
                <div className="flex flex-wrap gap-3 items-center">
                  {law.id && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-200">
                      📌 {law.id}
                    </span>
                  )}
                  {law.year && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                      📅 {law.year}
                    </span>
                  )}
                  {law.authority && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-sm font-medium border border-green-200">
                      🏛️ {law.authority}
                    </span>
                  )}
                  {law.type && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full text-sm font-medium border border-purple-200">
                      📋 {law.type}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Description Section */}
            {law.description && (
              <div className="p-6 space-y-2">
                <h2 className="text-lg font-semibold text-gray-800">
                  📝 Tóm tắt
                </h2>
                <p className="text-gray-700 leading-relaxed italic border-l-4 border-blue-300 pl-4">
                  {law.description}
                </p>
              </div>
            )}

            {/* Content Section */}
            {law.content && (
              <div className="p-6 space-y-3">
                <h2 className="text-lg font-semibold text-gray-800">
                  📄 Nội dung đầy đủ
                </h2>
                <div className="bg-gray-50 p-5 rounded-lg border border-gray-200 text-sm whitespace-pre-wrap text-gray-800 leading-relaxed max-h-96 overflow-y-auto">
                  {law.content.substring(0, 5000)}
                  {law.content.length > 5000 && (
                    <p className="text-xs text-gray-500 mt-4 italic">
                      ↓ Nội dung được cắt ngắn (xem file đầy đủ để biết toàn bộ)
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Previous Questions Section */}
            {questions.length > 0 && (
              <div className="p-6 space-y-3">
                <h2 className="text-lg font-semibold text-gray-800">
                  💬 Câu hỏi từ trước
                </h2>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {questions.map((q) => (
                    <div
                      key={q.id}
                      className="p-3 bg-gray-50 rounded border border-gray-200"
                    >
                      <p className="text-sm font-medium text-gray-900">
                        {q.question}
                      </p>
                      {q.answer && (
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          A: {q.answer}
                        </p>
                      )}
                      {q.tags && q.tags.length > 0 && (
                        <div className="flex gap-1 mt-2 flex-wrap">
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
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Chat Panel - Right Column */}
        <div className="col-span-1 h-full overflow-hidden">
          <ConsultantPanel
            context={law.content || law.description || ""}
            contextType="law-detail"
            lawId={id}
          />
        </div>
      </div>
    </MainLayout>
  );
}
