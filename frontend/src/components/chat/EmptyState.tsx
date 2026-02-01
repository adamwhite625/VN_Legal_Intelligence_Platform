import { Bot } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
      <div className="bg-primary/10 p-6 rounded-full">
        <Bot className="h-12 w-12 text-primary" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight">
        Trợ lý Pháp luật Việt Nam
      </h2>
      <p className="text-muted-foreground max-w-md">
        Tôi có thể tra cứu và giải đáp các tình huống dựa trên Bộ luật Dân sự,
        Hình sự, Lao động và Hôn nhân gia đình.
      </p>
    </div>
  );
}
