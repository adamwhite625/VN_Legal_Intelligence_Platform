import MainLayout from "@/shared/layout/MainLayout";
import ConsultantPanel from "../components/ConsultantPanel";

export default function GlobalConsultantPage() {
  return (
    <MainLayout>
      <div className="h-[calc(100vh-6rem)]">
        <ConsultantPanel context="" />
      </div>
    </MainLayout>
  );
}
