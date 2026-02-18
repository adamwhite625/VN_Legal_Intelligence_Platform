import { create } from "zustand";
import { searchLaws, type LawItem } from "../api/searchApi";

interface SearchState {
  keyword: string;
  results: LawItem[];
  loading: boolean;
  setKeyword: (k: string) => void;
  filterResults: () => Promise<void>;
}

export const useSearchStore = create<SearchState>((set, get) => ({
  keyword: "",
  results: [],
  loading: false,

  setKeyword: async (keyword) => {
    set({ keyword });
    await get().filterResults();
  },

  filterResults: async () => {
    const { keyword } = get();

    if (!keyword.trim()) {
      set({ results: [] });
      return;
    }

    set({ loading: true });

    try {
      const response = await searchLaws(
        keyword,
        undefined,
        undefined,
        undefined,
        undefined,
        20,
        "fast",
      );

      set({ results: response.results });
    } catch (error) {
      console.error("Search error:", error);
      set({ results: [] });
    } finally {
      set({ loading: false });
    }
  },
}));
