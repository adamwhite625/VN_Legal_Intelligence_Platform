import { create } from "zustand";
import { sendChatMessage } from "../api/consultantApi";

interface Message {
  sender: "user" | "assistant";
  text: string;
}

interface ConsultantState {
  messages: Message[];
  loading: boolean;
  sessions: Record<string, number>; // lawId -> sessionId
  sendMessage: (text: string, context: string, lawId: string) => Promise<void>;
  resetMessages: () => void;
}

export const useConsultantStore = create<ConsultantState>((set, get) => ({
  messages: [],
  loading: false,
  sessions: {},

  resetMessages: () => set({ messages: [] }),

  sendMessage: async (text, context, lawId) => {
    set((state) => ({
      messages: [...state.messages, { sender: "user", text }],
    }));

    set({ loading: true });

    try {
      const fullQuestion = context
        ? `${text}\n\nDựa trên văn bản sau:\n${context}`
        : text;

      const state = get();
      const sessionId = state.sessions[lawId];

      const data = await sendChatMessage(fullQuestion, sessionId);

      set((state) => ({
        messages: [
          ...state.messages,
          { sender: "assistant", text: data.answer },
        ],
        sessions: {
          ...state.sessions,
          [lawId]: data.session_id ?? sessionId,
        },
      }));
    } catch {
      set((state) => ({
        messages: [
          ...state.messages,
          {
            sender: "assistant",
            text: "Có lỗi khi kết nối AI.",
          },
        ],
      }));
    } finally {
      set({ loading: false });
    }
  },
}));
