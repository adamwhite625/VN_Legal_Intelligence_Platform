import SidebarHeader from "./SidebarHeader";
import SidebarSessionList from "./SidebarSessionList";
import SidebarUser from "./SidebarUser";
import type { Session } from "@/types";

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
    </aside>
  );
}
