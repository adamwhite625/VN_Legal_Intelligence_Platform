import Sidebar from "@/components/sidebar/Sidebar";
import ChatMessages from "@/components/chat/ChatMessages";
import ChatInput from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";
import { ScrollArea } from "@/components/ui/scroll-area";
import ChatHeader from "@/components/chat/ChatHeader";

export default function ChatPage() {
  const chat = useChat();

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar - Cột trái */}
      <div className="w-[280px] hidden md:block shrink-0 border-r">
        <Sidebar
          sessions={chat.sessions}
          currentSessionId={null}
          onSelect={chat.selectSession}
          onNew={() => {}}
        />
      </div>

      {/* Main Chat - Cột phải */}
      <div className="flex-1 flex flex-col min-h-0 min-w-0">
        {/* Header */}
        <ChatHeader />

        {/* Messages Area */}
        <div className="flex-1 min-h-0 overflow-hidden relative">
          <ScrollArea className="h-full">
            <div className="px-6 py-6">
              <ChatMessages messages={chat.messages} />
              <div ref={chat.scrollRef} className="h-4" />{" "}
              {/* Spacer cuối cùng */}
            </div>
          </ScrollArea>
        </div>

        {/* Input Area - SỬA ĐOẠN NÀY */}
        {/* Dùng đúng cấu trúc: h-[88px] border-t flex items-center */}
        <div className="h-[88px] border-t flex items-center px-6 bg-background shrink-0 z-10">
          <ChatInput
            value={chat.input}
            onChange={chat.setInput}
            onSend={chat.send}
            disabled={chat.loading}
          />
        </div>
      </div>
    </div>
  );
}
