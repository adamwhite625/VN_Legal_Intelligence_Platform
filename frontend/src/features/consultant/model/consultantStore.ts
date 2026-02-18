import { create } from "zustand";
import {
  sendChatMessage,
  startSession,
  getSessionHistory,
  type ChatResponse,
} from "../api/consultantApi";

interface Message {
  id?: number;
  sender: "user" | "assistant";
  text: string;
  sources?: string[];
}

interface ConsultantState {
  messages: Message[];
  loading: boolean;
  currentSessionId: number | null;
  contextType: "general" | "law-detail";
  currentLawId: string | null;

  sendMessage: (
    text: string,
    context?: string,
    lawId?: string,
  ) => Promise<void>;
  resetMessages: () => void;
  initSession: (
    contextType?: "general" | "law-detail",
    lawId?: string,
  ) => Promise<void>;
  loadSessionHistory: (sessionId: number) => Promise<void>;
}

export const useConsultantStore = create<ConsultantState>((set, get) => ({
  messages: [],
  loading: false,
  currentSessionId: null,
  contextType: "general",
  currentLawId: null,

  resetMessages: () => set({ messages: [] }),

  initSession: async (contextType = "general", lawId) => {
    try {
      const session = await startSession(contextType, lawId);
      set({
        currentSessionId: session.id,
        contextType,
        currentLawId: lawId || null,
        messages: [],
      });
    } catch (error) {
      console.error("Failed to init session:", error);
    }
  },

  loadSessionHistory: async (sessionId) => {
    try {
      const history = await getSessionHistory(sessionId);
      const messages: Message[] = history.messages.map((msg) => ({
        id: msg.id,
        sender: msg.sender,
        text: msg.message,
        sources: msg.sources || [],
      }));
      set({
        messages,
        currentSessionId: sessionId,
        contextType: history.session_type as any,
        currentLawId: history.law_id || null,
      });
    } catch (error) {
      console.error("Failed to load session history:", error);
    }
  },

  sendMessage: async (text, context, lawId) => {
    set((state) => ({
      messages: [...state.messages, { sender: "user", text }],
    }));

    set({ loading: true });

    try {
      const state = get();

      // Init session if not exists
      if (!state.currentSessionId) {
        const session = await startSession(
          state.contextType,
          lawId || state.currentLawId || undefined,
        );
        set({ currentSessionId: session.id });
      }

      const fullQuestion = context
        ? `${text}\n\nDựa trên văn bản sau:\n${context}`
        : text;

      const data: ChatResponse = await sendChatMessage(
        fullQuestion,
        state.contextType,
        state.currentSessionId || undefined,
        state.currentLawId || lawId || undefined,
      );

      set((state) => ({
        messages: [
          ...state.messages,
          {
            id: data.message_id,
            sender: "assistant",
            text: data.answer,
            sources: data.sources || [],
          },
        ],
        currentSessionId: data.session_id,
      }));
    } catch (error) {
      console.error("Chat error:", error);
      set((state) => ({
        messages: [
          ...state.messages,
          {
            sender: "assistant",
            text: "Có lỗi khi kết nối AI. Vui lòng thử lại!",
          },
        ],
      }));
    } finally {
      set({ loading: false });
    }
  },
}));
