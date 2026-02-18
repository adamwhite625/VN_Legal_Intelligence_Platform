import { create } from "zustand";
import {
  saveLaw,
  unsaveLaw,
  isLawSaved,
  getSavedLaws,
  saveQuestion,
  updateQuestion,
  deleteQuestion,
  getSavedQuestions,
  getQuestionsForLaw,
  getTrackingStats,
  type SavedLaw,
  type SavedQuestion,
} from "../api/searchApi";

interface TrackingStats {
  total_saved_laws: number;
  total_saved_questions: number;
  total_sessions: number;
  recent_sessions: Array<{
    id: number;
    session_type: string;
    law_id?: string;
    title?: string;
    created_at: string;
  }>;
}

interface TrackingState {
  // Saved Laws
  savedLaws: SavedLaw[];
  isSaving: boolean;

  // Saved Questions
  savedQuestions: SavedQuestion[];
  questionsForCurrentLaw: SavedQuestion[];

  // Stats
  stats: TrackingStats | null;

  // Actions
  saveLaw: (
    lawId: string,
    lawTitle: string,
    lawType?: string,
    lawYear?: string,
    lawAuthority?: string,
    lawContent?: string,
    notes?: string,
  ) => Promise<SavedLaw>;
  unsaveLaw: (lawId: string) => Promise<void>;
  checkLawSaved: (lawId: string) => Promise<boolean>;
  loadSavedLaws: (skip?: number, limit?: number) => Promise<void>;

  saveQuestion: (
    question: string,
    answer?: string,
    lawId?: string,
    tags?: string[],
  ) => Promise<SavedQuestion>;
  updateQuestion: (
    questionId: number,
    answer?: string,
    tags?: string[],
    isBookmarked?: boolean,
  ) => Promise<SavedQuestion>;
  deleteQuestion: (questionId: number) => Promise<void>;
  loadSavedQuestions: (
    lawId?: string,
    skip?: number,
    limit?: number,
  ) => Promise<void>;
  loadQuestionsForLaw: (lawId: string) => Promise<void>;

  loadStats: () => Promise<void>;
  clearQuestionsForCurrentLaw: () => void;
}

export const useTrackingStore = create<TrackingState>((set) => ({
  savedLaws: [],
  isSaving: false,
  savedQuestions: [],
  questionsForCurrentLaw: [],
  stats: null,

  // ============= SAVED LAWS =============

  saveLaw: async (
    lawId,
    lawTitle,
    lawType,
    lawYear,
    lawAuthority,
    lawContent,
    notes,
  ) => {
    set({ isSaving: true });
    try {
      const result = await saveLaw(
        lawId,
        lawTitle,
        lawType,
        lawYear,
        lawAuthority,
        lawContent,
        notes,
      );
      set((state) => ({
        savedLaws: [result, ...state.savedLaws],
      }));
      return result;
    } finally {
      set({ isSaving: false });
    }
  },

  unsaveLaw: async (lawId) => {
    await unsaveLaw(lawId);
    set((state) => ({
      savedLaws: state.savedLaws.filter((law) => law.law_id !== lawId),
    }));
  },

  checkLawSaved: async (lawId) => {
    return await isLawSaved(lawId);
  },

  loadSavedLaws: async (skip = 0, limit = 100) => {
    try {
      const laws = await getSavedLaws(skip, limit);
      set({ savedLaws: laws });
    } catch (error) {
      console.error("Failed to load saved laws:", error);
    }
  },

  // ============= SAVED QUESTIONS =============

  saveQuestion: async (question, answer, lawId, tags) => {
    set({ isSaving: true });
    try {
      const result = await saveQuestion(question, answer, lawId, tags);
      set((state) => ({
        savedQuestions: [result, ...state.savedQuestions],
      }));
      return result;
    } finally {
      set({ isSaving: false });
    }
  },

  updateQuestion: async (questionId, answer, tags, isBookmarked) => {
    const result = await updateQuestion(questionId, answer, tags, isBookmarked);
    set((state) => ({
      savedQuestions: state.savedQuestions.map((q) =>
        q.id === questionId ? result : q,
      ),
      questionsForCurrentLaw: state.questionsForCurrentLaw.map((q) =>
        q.id === questionId ? result : q,
      ),
    }));
    return result;
  },

  deleteQuestion: async (questionId) => {
    await deleteQuestion(questionId);
    set((state) => ({
      savedQuestions: state.savedQuestions.filter((q) => q.id !== questionId),
      questionsForCurrentLaw: state.questionsForCurrentLaw.filter(
        (q) => q.id !== questionId,
      ),
    }));
  },

  loadSavedQuestions: async (lawId, skip = 0, limit = 100) => {
    try {
      const questions = await getSavedQuestions(lawId, skip, limit);
      set({ savedQuestions: questions });
    } catch (error) {
      console.error("Failed to load saved questions:", error);
    }
  },

  loadQuestionsForLaw: async (lawId) => {
    try {
      const questions = await getQuestionsForLaw(lawId);
      set({ questionsForCurrentLaw: questions });
    } catch (error) {
      console.error("Failed to load questions for law:", error);
    }
  },

  clearQuestionsForCurrentLaw: () => {
    set({ questionsForCurrentLaw: [] });
  },

  // ============= STATS =============

  loadStats: async () => {
    try {
      const stats = await getTrackingStats();
      set({ stats });
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  },
}));
