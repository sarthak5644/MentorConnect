/**
 * The backend stores qualifications/achievements as a raw JSON string on
 * the mentor record (not a real array), so every place that reads them
 * needs to parse it defensively — it may be null, empty, or malformed.
 */
export function parseJsonList<T>(raw: string | null | undefined): T[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}