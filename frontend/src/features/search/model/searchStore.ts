import { create } from "zustand";
import { mockLaws, type LawItem } from "./mockData";

interface SearchState {
  keyword: string;
  type: string;
  year: string;
  authority: string;
  results: LawItem[];
  setKeyword: (k: string) => void;
  setFilter: (field: string, value: string) => void;
  filterResults: () => void;
}

export const useSearchStore = create<SearchState>((set, get) => ({
  keyword: "",
  type: "",
  year: "",
  authority: "",
  results: mockLaws,

  setKeyword: (keyword) => {
    set({ keyword });
    get().filterResults();
  },

  setFilter: (field, value) => {
    set({ [field]: value } as any);
    get().filterResults();
  },

  filterResults: () => {
    const { keyword, type, year, authority } = get();

    const filtered = mockLaws.filter((law) => {
      return (
        law.title.toLowerCase().includes(keyword.toLowerCase()) &&
        (type === "" || law.type === type) &&
        (year === "" || law.year === year) &&
        (authority === "" || law.authority === authority)
      );
    });

    set({ results: filtered });
  },
}));
