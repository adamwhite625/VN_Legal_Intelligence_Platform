import { useState } from "react";
import MainLayout from "@/shared/layout/MainLayout";
import ConsultantPanel from "../components/ConsultantPanel";
import SessionHistoryPanel from "../components/SessionHistoryPanel";
import { useConsultantStore } from "../model/consultantStore";

export default function GlobalConsultantPage() {
  const { loadSessionHistory } = useConsultantStore();
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
    null,
  );

  const handleSelectSession = async (sessionId: number) => {
    setSelectedSessionId(sessionId);
    await loadSessionHistory(sessionId);
  };

  return (
    <MainLayout>
      <div className="h-[calc(100vh-6rem)] grid grid-cols-3 gap-6">
        {/* Chat Panel */}
        <div className="col-span-2">
          <ConsultantPanel context="" contextType="general" />
        </div>

        {/* Session History Panel */}
        <div>
          <SessionHistoryPanel onSelectSession={handleSelectSession} />
        </div>
      </div>
    </MainLayout>
  );
}
