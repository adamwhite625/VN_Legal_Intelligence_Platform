import { MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Session } from "@/types";

export default function SidebarSessionItem({
  session,
  active,
  onClick,
}: {
  session: Session;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
        active
          ? "bg-muted font-medium"
          : "hover:bg-muted/60 text-muted-foreground",
      )}
    >
      <MessageSquare className="h-4 w-4 shrink-0" />
      <span className="truncate">
        {session.first_message || `Chat #${session.id}`}
      </span>
    </div>
  );
}
