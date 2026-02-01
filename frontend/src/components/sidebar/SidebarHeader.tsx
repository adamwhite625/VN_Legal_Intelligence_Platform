import { Scale, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SidebarHeader({ onNew }: { onNew: () => void }) {
  return (
    <div className="border-b p-4 space-y-3">
      <div className="flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Scale className="h-5 w-5" />
        </div>
        <div className="leading-tight">
          <div className="font-semibold">Luật Sư AI</div>
          <div className="text-xs text-muted-foreground">
            Trợ lý pháp luật VN
          </div>
        </div>
      </div>

      <Button
        onClick={onNew}
        className="w-full justify-start gap-2"
        variant="secondary"
      >
        <Plus className="h-4 w-4" />
        Cuộc trò chuyện mới
      </Button>
    </div>
  );
}
