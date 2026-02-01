import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

export default function ChatInput({
  value,
  onChange,
  onSend,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
}) {
  return (
    <div className="relative w-full">
      {" "}
      {/* Thêm w-full */}
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSend()}
        disabled={disabled}
        placeholder="Nhập câu hỏi pháp lý..."
        // SỬA: Dùng h-14 thay vì py-6 để chiều cao chuẩn 56px
        className="pr-12 h-14 text-base shadow-sm"
      />
      <Button
        size="icon"
        onClick={onSend}
        disabled={disabled || !value.trim()}
        // Căn chỉnh nút gửi vào giữa ô input
        className="absolute right-2 top-2 h-10 w-10"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
