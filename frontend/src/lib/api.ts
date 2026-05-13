import type { LocationsResponse, RecommendationRequest, RecommendationResponse } from "@/lib/types";

function apiBase(): string {
  const b = process.env.NEXT_PUBLIC_API_URL?.trim();
  return b && b.length > 0 ? b.replace(/\/$/, "") : "http://127.0.0.1:8000";
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: unknown };
    const d = data.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      const parts = d
        .map((x) => {
          if (x && typeof x === "object" && "msg" in x) return String((x as { msg: unknown }).msg);
          return JSON.stringify(x);
        })
        .filter(Boolean);
      if (parts.length) return parts.join("; ");
    }
  } catch {
    /* ignore */
  }
  return await res.text().catch(() => res.statusText);
}

export async function getLocations(): Promise<LocationsResponse> {
  const res = await fetch(`${apiBase()}/api/locations`, { cache: "no-store" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<LocationsResponse>;
}

export async function postRecommendations(
  body: RecommendationRequest,
): Promise<RecommendationResponse> {
  const res = await fetch(`${apiBase()}/api/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json() as Promise<RecommendationResponse>;
}

export async function getHealth(): Promise<Record<string, unknown>> {
  const res = await fetch(`${apiBase()}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<Record<string, unknown>>;
}
