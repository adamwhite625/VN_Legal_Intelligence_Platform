import { create } from "zustand";
import {
  streamChatMessage,
  startSession,
  getSessionHistory,
  getSessions,
  deleteSession,
} from "../api/consultantApi";

interface Message {
  id?: number;
  sender: "user" | "assistant";
  text: string;
  sources?: string[];
}

interface SessionListItem {
  id: number;
  session_type: string;
  law_id?: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

interface ConsultantState {
  messages: Message[];
  sessions: SessionListItem[];
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
  setupContext: (
    contextType?: "general" | "law-detail",
    lawId?: string,
  ) => void; // Changed: just setup context, don't create session
  loadSessionHistory: (sessionId: number) => Promise<void>;
  loadSessions: (skip?: number, limit?: number) => Promise<void>;
  removeSessions: (sessionId: number) => Promise<void>;
}

export const useConsultantStore = create<ConsultantState>((set, get) => ({
  messages: [],
  sessions: [],
  loading: false,
  currentSessionId: null,
  contextType: "general",
  currentLawId: null,

  resetMessages: () => set({ messages: [] }),

  loadSessions: async (skip = 0, limit = 100) => {
    try {
      const sessions = await getSessions(skip, limit);
      set({ sessions });
    } catch (error) {
      console.error("Failed to load sessions:", error);
    }
  },

  removeSessions: async (sessionId: number) => {
    try {
      await deleteSession(sessionId);
      // Reload sessions after deletion
      const state = get();
      await state.loadSessions();
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  },

  // Changed: Just setup context without creating session
  setupContext: (contextType = "general", lawId) => {
    set({
      contextType,
      currentLawId: lawId || null,
      messages: [], // Clear messages when switching context
    });
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

      // Create session only when sending first message (lazy creation)
      let sessionId = state.currentSessionId;
      if (!sessionId) {
        const session = await startSession(
          state.contextType,
          lawId || state.currentLawId || undefined,
        );
        sessionId = session.id;
        set({ currentSessionId: sessionId });
      }

      const fullQuestion = context
        ? `${text}\n\nDựa trên văn bản sau:\n${context}`
        : text;

      // Create a temporary message for the assistant
      const tempMessageId = Date.now();
      set((state) => ({
        messages: [
          ...state.messages,
          {
            id: tempMessageId,
            sender: "assistant",
            text: "",
            sources: [],
          },
        ],
      }));

      const onChunk = (chunk: string) => {
        set((state) => {
          const newMessages = [...state.messages];
          const assistantMessageIndex = newMessages.findIndex(
            (m) => m.id === tempMessageId
          );
          if (assistantMessageIndex !== -1) {
            newMessages[assistantMessageIndex].text += chunk;
          }
          return { messages: newMessages };
        });
      };

      const result = await streamChatMessage(
        fullQuestion,
        onChunk,
        state.contextType,
        sessionId,
        state.currentLawId || lawId || undefined,
      );

      set((state) => {
        const newMessages = [...state.messages];
        const assistantMessageIndex = newMessages.findIndex(
          (m) => m.id === tempMessageId
        );
        if (assistantMessageIndex !== -1) {
          // Finalize message with actual DB ID and sources
          newMessages[assistantMessageIndex].id = result.messageId;
          newMessages[assistantMessageIndex].sources = result.sources || [];
        }
        return {
          messages: newMessages,
          currentSessionId: result.sessionId,
        };
      });
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
