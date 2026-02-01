export interface Message {
  sender: "user" | "assistant";
  message: string;
  sources?: string[];
}

export interface Session {
  id: number;
  first_message?: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}
