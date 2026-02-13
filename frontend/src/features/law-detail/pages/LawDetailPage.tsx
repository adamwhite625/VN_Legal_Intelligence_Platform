import { useParams } from "react-router-dom";
import MainLayout from "@/shared/layout/MainLayout";
import { mockLaws } from "@/features/search/model/mockData";
import { useLocation } from "react-router-dom";
import { highlightText } from "@/shared/utils/highlightText";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import ConsultantPanel from "@/features/consultant/components/ConsultantPanel";

export default function LawDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const keyword = params.get("keyword") || "";
  const navigate = useNavigate();

  const law = mockLaws.find((item) => item.id === Number(id));

  if (!law) {
    return (
      <MainLayout>
        <div className="p-6">Không tìm thấy văn bản</div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="grid grid-cols-3 gap-6 h-[calc(100vh-6rem)]">
        {/* Law Detail */}
        <div className="col-span-2 overflow-y-auto">
          <div className="bg-white p-6 rounded-xl shadow space-y-4">
            <button
              onClick={() => navigate("/")}
              className="text-blue-600 hover:underline"
            >
              ← Quay lại kết quả tìm kiếm
            </button>

            <h1 className="text-2xl font-bold">{law.title}</h1>

            <div
              dangerouslySetInnerHTML={{
                __html: highlightText(law.description, keyword),
              }}
            />
          </div>
        </div>

        {/* AI Panel */}
        <div className="col-span-1 h-full">
          <ConsultantPanel context={law.description} />
        </div>
      </div>
    </MainLayout>
  );
}
