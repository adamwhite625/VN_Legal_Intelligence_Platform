import MainLayout from "@/shared/layout/MainLayout";
import ConsultantPanel from "../components/ConsultantPanel";

export default function GlobalConsultantPage() {
  return (
    <MainLayout>
      <div className="h-[calc(100vh-6rem)] grid grid-cols-3 gap-6">
        {/* Chat Panel */}
        <div className="col-span-2">
          <ConsultantPanel context="" contextType="general" />
        </div>

        {/* Tracking Panel */}
        <div className="bg-white rounded-xl shadow p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">Lịch sử</h3>
          <div className="text-sm text-gray-500 space-y-4">
            <div>
              <p className="font-medium text-gray-700 mb-2">Câu hỏi đã lưu</p>
              <p className="text-xs">Hiển thị các câu hỏi bạn đã lưu</p>
            </div>
            <div>
              <p className="font-medium text-gray-700 mb-2">📖 Luật đã lưu</p>
              <p className="text-xs">Hiển thị các luật bạn đã lưu</p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
