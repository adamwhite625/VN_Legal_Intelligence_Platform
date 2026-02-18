import axiosInstance from "@/shared/api/axiosInstance";

export interface LawItem {
  id?: string;
  title: string;
  type: string;
  year?: string;
  authority?: string;
  description?: string;
  content?: string;
  articles?: string[];
}

export interface SearchResponse {
  results: LawItem[];
  total: number;
  filters_applied?: {
    law_name?: string;
    document_type?: string;
    article_number?: string;
    year?: string;
  };
}

export interface SavedLaw {
  id: number;
  law_id: string;
  law_title: string;
  law_type?: string;
  law_year?: string;
  law_authority?: string;
  notes?: string;
  slug?: string;
  created_at: string;
}

export interface SavedQuestion {
  id: number;
  question: string;
  answer?: string;
  law_id?: string;
  tags?: string[];
  is_bookmarked: boolean;
  created_at: string;
}

// ============= SEARCH API =============

export async function searchLaws(
  keyword: string,
  type_filter?: string,
  year_filter?: string,
  authority_filter?: string,
  article_filter?: string,
  limit: number = 20,
  mode: "fast" | "semantic" = "fast",
): Promise<SearchResponse> {
  const response = await axiosInstance.post("/search/search", null, {
    params: {
      keyword,
      mode,
      type_filter,
      year_filter,
      authority_filter,
      article_filter,
      limit,
    },
  });

  return response.data;
}

export async function getLawDetail(
  lawId: string,
  source: "auto" | "json" | "qdrant" = "auto",
): Promise<LawItem> {
  const response = await axiosInstance.get(
    `/search/laws/${encodeURIComponent(lawId)}`,
    { params: { source } },
  );
  return response.data;
}

// ============= SAVE LAW API =============

export async function saveLawAndCreateSession(
  lawId: string,
): Promise<{
  message: string;
  saved_law_id: number;
  slug?: string;
  session_id: number;
}> {
  const response = await axiosInstance.post(
    `/search/laws/${encodeURIComponent(lawId)}/save`,
  );
  return response.data;
}

// ============= TRACKING API =============

export async function saveLaw(
  lawId: string,
  lawTitle: string,
  lawType?: string,
  lawYear?: string,
  lawAuthority?: string,
  lawContent?: string,
  notes?: string,
): Promise<SavedLaw> {
  const response = await axiosInstance.post("/tracking/laws/save", {
    law_id: lawId,
    law_title: lawTitle,
    law_type: lawType,
    law_year: lawYear,
    law_authority: lawAuthority,
    law_content: lawContent,
    notes,
  });
  return response.data;
}

export async function unsaveLaw(lawId: string): Promise<void> {
  await axiosInstance.delete(
    `/tracking/laws/${encodeURIComponent(lawId)}/unsave`,
  );
}

export async function isLawSaved(lawId: string): Promise<boolean> {
  const response = await axiosInstance.get(
    `/tracking/laws/is-saved/${encodeURIComponent(lawId)}`,
  );
  return response.data.is_saved;
}

export async function getSavedLaws(
  skip: number = 0,
  limit: number = 100,
): Promise<SavedLaw[]> {
  const response = await axiosInstance.get("/tracking/laws", {
    params: { skip, limit },
  });
  return response.data;
}

// ============= QUESTIONS API =============

export async function saveQuestion(
  question: string,
  answer?: string,
  lawId?: string,
  tags?: string[],
): Promise<SavedQuestion> {
  const response = await axiosInstance.post("/tracking/questions", {
    question,
    answer,
    law_id: lawId,
    tags,
  });
  return response.data;
}

export async function updateQuestion(
  questionId: number,
  answer?: string,
  tags?: string[],
  isBookmarked?: boolean,
): Promise<SavedQuestion> {
  const response = await axiosInstance.put(
    `/tracking/questions/${questionId}`,
    {
      answer,
      tags,
      is_bookmarked: isBookmarked,
    },
  );
  return response.data;
}

export async function deleteQuestion(questionId: number): Promise<void> {
  await axiosInstance.delete(`/tracking/questions/${questionId}`);
}

export async function getSavedQuestions(
  lawId?: string,
  skip: number = 0,
  limit: number = 100,
): Promise<SavedQuestion[]> {
  const response = await axiosInstance.get("/tracking/questions", {
    params: { law_id: lawId, skip, limit },
  });
  return response.data;
}

export async function getQuestionsForLaw(
  lawId: string,
): Promise<SavedQuestion[]> {
  const response = await axiosInstance.get(
    `/tracking/laws/${encodeURIComponent(lawId)}/questions`,
  );
  return response.data;
}

// ============= TRACKING STATS API =============

export async function getTrackingStats(): Promise<{
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
}> {
  const response = await axiosInstance.get("/tracking/stats");
  return response.data;
}
