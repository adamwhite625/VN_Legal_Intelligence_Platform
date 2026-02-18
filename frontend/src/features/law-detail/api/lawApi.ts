import axiosInstance from "@/shared/api/axiosInstance";

export interface LawDetail {
  law_id: string;
  law_name: string;
  article_title?: string;
  law_content?: string;
  source_doc_id?: string;
  origin_url?: string;
  summary?: string;
}

/**
 * Get law detail by law_id and/or law_name.
 * Backend expected route: GET /law/detail?law_id=...&law_name=...
 */
export async function getLawDetailById(lawId: string, lawName?: string) {
  const params: Record<string, string> = { law_id: lawId };
  if (lawName) params["law_name"] = lawName;

  const resp = await axiosInstance.get("/law/detail", { params });
  return resp.data as LawDetail;
}

/**
 * Optional: send click tracking for analytics
 * Backend may not have this endpoint yet; see server-side note.
 */
export async function trackLawClick(payload: {
  law_id: string;
  source?: string;
}) {
  // If backend does not provide /law/track_click, this will fail.
  // It's safe to call this in a try/catch from the frontend.
  return axiosInstance.post("/law/track_click", payload);
}
