import { create } from "zustand";
import { searchLaws, type LawItem } from "../api/searchApi";

interface SearchState {
  keyword: string;
  results: LawItem[];
  loading: boolean;
  loadingMore: boolean;
  currentPage: number;
  skip: number;
  hasMore: boolean;
  setKeyword: (k: string) => void;
  setCurrentPage: (page: number) => void;
  loadMore: () => Promise<void>;
  filterResults: () => Promise<void>;
}

const ITEMS_PER_PAGE = 20;

export const useSearchStore = create<SearchState>((set, get) => ({
  keyword: "",
  results: [],
  loading: false,
  loadingMore: false,
  currentPage: 1,
  skip: 0,
  hasMore: true,

  setKeyword: async (keyword) => {
    set({ keyword, currentPage: 1, skip: 0, results: [], hasMore: true });
    await get().filterResults();
  },

  setCurrentPage: (page: number) => {
    set({ currentPage: page });
  },

  loadMore: async () => {
    const { keyword, skip, results } = get();

    if (!keyword.trim() || !get().hasMore) {
      return;
    }

    set({ loadingMore: true });

    try {
      const newSkip = skip + ITEMS_PER_PAGE;
      const response = await searchLaws(
        keyword,
        undefined,
        undefined,
        undefined,
        undefined,
        newSkip,
        ITEMS_PER_PAGE,
        "fast",
      );

      const newResults = [...results, ...response.results];
      const hasMore = response.results.length === ITEMS_PER_PAGE;

      set({
        results: newResults,
        skip: newSkip,
        hasMore,
      });
    } catch (error) {
      console.error("Load more error:", error);
    } finally {
      set({ loadingMore: false });
    }
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
        0,
        ITEMS_PER_PAGE,
        "fast",
      );

      const hasMore = response.results.length === ITEMS_PER_PAGE;

      set({
        results: response.results,
        hasMore,
        skip: 0,
      });
    } catch (error) {
      console.error("Search error:", error);
      set({ results: [] });
    } finally {
      set({ loading: false });
    }
  },
}));
