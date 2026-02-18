import { mockLaws } from "@/features/search/model/mockData";

export function findLawIdFromSource(source: string): number | string | null {
  const docMatch = source.match(/doc:([a-zA-Z0-9_\-]+)/i);
  if (docMatch) return docMatch[1];

  for (const law of mockLaws) {
    if (source.includes(law.title)) {
      return law.id; // mock data uses numeric id
    }
  }

  const articleMatch = source.match(/Điều\s*(\d+)/i);
  if (articleMatch) {
    return `article:${articleMatch[1]}`;
  }

  return null;
}
