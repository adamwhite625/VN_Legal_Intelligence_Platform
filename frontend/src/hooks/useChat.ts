import { useState, useRef, useEffect } from "react";
import * as api from "@/services/chatApi";
import type { Message, Session } from "@/types";

export function useChat() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.fetchSessions().then((res) => setSessions(res.data));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const selectSession = async (id: number) => {
    setCurrentSessionId(id);
    setLoading(true);
    const res = await api.fetchHistory(id);
    setMessages(res.data);
    setLoading(false);
  };

  const send = async () => {
    if (!input.trim()) return;

    let sessionId = currentSessionId;
    if (!sessionId) {
      const res = await api.createSession();
      sessionId = res.data.id;
      setSessions((prev) => [res.data, ...prev]);
      setCurrentSessionId(sessionId);
    }

    const userText = input;
    setInput("");
    setMessages((prev) => [...prev, { sender: "user", message: userText }]);
    setLoading(true);

    try {
      const res = await api.sendMessage({
        query: userText,
        session_id: sessionId,
      });
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          message: res.data.answer,
          sources: res.data.sources,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return {
    sessions,
    messages,
    input,
    loading,
    scrollRef,
    setInput,
    selectSession,
    send,
    setSessions,
    setCurrentSessionId,
  };
}
