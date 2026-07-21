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

export async function streamChatMessage(
  message: string,
  onChunk: (chunk: string) => void,
  contextType: "general" | "law-detail" = "general",
  sessionId?: number,
  lawId?: string,
): Promise<{ sessionId: number; messageId: number; sources: string[] }> {
  // Use native fetch to handle the stream
  const token = localStorage.getItem("access_token"); // Adjust if your auth token is stored differently
  
  const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/chat/send-stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      query: message,
      session_id: sessionId || null,
      context_type: contextType,
      law_id: lawId || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Response body is null");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let done = false;
  
  let finalSessionId = sessionId || 0;
  let finalMessageId = 0;
  let finalSources: string[] = [];

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");
      
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const dataStr = line.slice("data: ".length).trim();
          if (!dataStr) continue;
          
          try {
            const data = JSON.parse(dataStr);
            
            if (data.type === "init") {
              finalSessionId = data.session_id;
            } else if (data.type === "chunk") {
              onChunk(data.content);
            } else if (data.type === "done") {
              finalSources = data.sources;
              finalMessageId = data.message_id;
            } else if (data.type === "error") {
              throw new Error(data.message);
            }
          } catch (e) {
            console.error("Error parsing stream JSON:", e);
          }
        }
      }
    }
  }

  return {
    sessionId: finalSessionId,
    messageId: finalMessageId,
    sources: finalSources,
  };
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
