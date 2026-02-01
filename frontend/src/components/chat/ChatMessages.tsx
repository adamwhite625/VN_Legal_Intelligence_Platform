import ChatMessageItem from "./ChatMessageItem";
import EmptyState from "./EmptyState";
import type { Message } from "@/types";

export default function ChatMessages({ messages }: { messages: Message[] }) {
  if (!messages.length) return <EmptyState />;

  return (
    <div className="space-y-6">
      {messages.map((msg, i) => (
        <ChatMessageItem key={i} message={msg} />
      ))}
    </div>
  );
}
