import axiosInstance from "@/shared/api/axiosInstance";

export interface ChatMessage {
  id: number;
  sender: "user" | "assistant";
  message: string;
  sources?: string[];
  created_at: string;
}

export interface ChatSession {
  id: number;
  session_type: "general" | "law-detail";
  law_id?: string;
  title?: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface MessageSummary {
  id: number;
  summary: string;
  message_count: number;
  summarized_at: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  session_id: number;
  message_id: number;
}

// ============= CHAT MESSAGE API =============

export async function sendChatMessage(
  message: string,
  contextType: "general" | "law-detail" = "general",
  sessionId?: number,
  lawId?: string,
): Promise<ChatResponse> {
  const response = await axiosInstance.post("/chat/send", {
    query: message,
    session_id: sessionId || null,
    context_type: contextType,
    law_id: lawId || null,
  });

  return response.data;
}

// ============= SESSION API =============

export async function startSession(
  sessionType: "general" | "law-detail" = "general",
  lawId?: string,
): Promise<{
  id: number;
  session_type: string;
  law_id?: string;
  title?: string;
}> {
  const response = await axiosInstance.post("/chat/session/start", null, {
    params: { session_type: sessionType, law_id: lawId || null },
  });
  return response.data;
}

export async function getSessions(
  skip: number = 0,
  limit: number = 100,
): Promise<
  Array<{
    id: number;
    session_type: string;
    law_id?: string;
    title?: string;
    created_at: string;
    updated_at: string;
  }>
> {
  const response = await axiosInstance.get("/chat/sessions", {
    params: { skip, limit },
  });
  return response.data;
}

export async function deleteSession(sessionId: number): Promise<void> {
  await axiosInstance.delete(`/chat/session/${sessionId}`);
}

// ============= HISTORY API =============

export async function getSessionHistory(
  sessionId: number,
): Promise<ChatSession> {
  const response = await axiosInstance.get(`/chat/history/${sessionId}`);
  return response.data;
}

export async function getSessionSummaries(
  sessionId: number,
): Promise<MessageSummary[]> {
  const response = await axiosInstance.get(`/chat/summaries/${sessionId}`);
  return response.data;
}
