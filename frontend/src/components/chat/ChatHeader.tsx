import { Scale } from "lucide-react";

export default function ChatHeader() {
  return (
    <div className="border-b bg-background">
      <div className="mx-auto max-w-3xl px-4 py-3 flex items-center gap-3">
        {/* Quốc huy / biểu trưng */}
        <img
          src="/vn-emblem.jpg"
          alt="Cộng hòa Xã hội Chủ nghĩa Việt Nam"
          className="h-10 w-10 object-contain"
        />

        <div className="leading-tight">
          <div className="text-sm font-semibold uppercase tracking-wide">
            Cộng hòa Xã hội Chủ nghĩa Việt Nam
          </div>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Scale className="h-3 w-3" />
            Trợ lý tư vấn pháp luật AI (tham khảo)
          </div>
        </div>
      </div>
    </div>
  );
}
