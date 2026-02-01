import { ScrollArea } from "@/components/ui/scroll-area";
import SidebarSessionItem from "./SidebarSessionItem";
import type { Session } from "@/types";

interface Props {
  sessions: Session[];
  currentSessionId: number | null;
  onSelect: (id: number) => void;
}

export default function SidebarSessionList({
  sessions,
  currentSessionId,
  onSelect,
}: Props) {
  return (
    <ScrollArea className="h-full px-2 py-3">
      <div className="space-y-1">
        {sessions.map((s) => (
          <SidebarSessionItem
            key={s.id}
            session={s}
            active={s.id === currentSessionId}
            onClick={() => onSelect(s.id)}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
