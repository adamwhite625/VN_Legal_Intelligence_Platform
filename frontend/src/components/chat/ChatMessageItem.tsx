import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, BookOpen } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import type { Message } from "@/types";

export default function ChatMessageItem({ message }: { message: Message }) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {/* Bot Avatar */}
      {!isUser && (
        <Avatar className="h-8 w-8 border">
          <AvatarImage src="/bot-avatar.png" />
          <AvatarFallback className="bg-green-600 text-white">
            <Bot className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className="flex flex-col max-w-[85%] md:max-w-[75%] space-y-2">
        <Card
          className={`p-4 ${
            isUser
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-muted/50 dark:bg-zinc-900"
          }`}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none break-words leading-normal">
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.message}</p>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.message}
              </ReactMarkdown>
            )}
          </div>
        </Card>

        {/* Hiển thị nguồn (chỉ cho Bot) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="text-xs text-muted-foreground bg-muted/30 px-3 py-2 rounded border border-dashed">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="flex items-center gap-1 font-semibold whitespace-nowrap">
                <BookOpen className="h-3 w-3" /> Nguồn tham khảo:
              </span>
              <div className="flex gap-1.5 flex-wrap">
                {message.sources.map((src, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-background border rounded text-xs whitespace-nowrap"
                  >
                    {src}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <Avatar className="h-8 w-8 border">
          <AvatarFallback className="bg-blue-600 text-white">
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
