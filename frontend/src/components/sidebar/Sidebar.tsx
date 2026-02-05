import SidebarHeader from "./SidebarHeader";
import SidebarSessionList from "./SidebarSessionList";
import SidebarUser from "./SidebarUser";
import type { Session } from "@/types";
import { useAuth } from "@/context/AuthContext";

interface Props {
  sessions: Session[];
  currentSessionId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
}

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelect,
  onNew,
}: Props) {
  const { user } = useAuth();
  return (
    <aside className="w-72 h-full flex flex-col border-r bg-background">
      {/* Header */}
      <SidebarHeader onNew={onNew} />

      {/* Sessions */}
      <SidebarSessionList
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelect={onSelect}
      />

      {/* User */}
      <SidebarUser />
      {user?.role === "admin" && (
        <div className="p-4 border-t bg-red-50 text-red-600 font-bold">
          Admin Dashboard
        </div>
      )}
    </aside>
  );
}
