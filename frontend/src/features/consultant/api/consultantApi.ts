import axiosInstance from "@/shared/api/axiosInstance";

export async function sendChatMessage(message: string, sessionId?: number) {
  const response = await axiosInstance.post("/chat/send", {
    query: message,
    session_id: sessionId || null,
  });

  return response.data;
}
