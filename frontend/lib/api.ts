import { getAuthToken } from "./authStorage";
import { apiBaseUrl } from "./config";

function authHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const t = getAuthToken();
  if (!t) return {};
  return { Authorization: `Bearer ${t}` };
}

/** Thrown by `getJson` / `postJson` / `patchJson` when `response.ok` is false. */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Turn FastAPI-style JSON bodies into a short string for UI and logs. */
export function formatApiErrorMessage(status: number, body: string): string {
  const trimmed = (body || "").trim();
  if (!trimmed) {
    if (status === 401) return "Session missing or expired. Sign in again.";
    if (status === 404) return "Not found (404).";
    return `Request failed (${status}).`;
  }
  try {
    const j = JSON.parse(trimmed) as { detail?: unknown };
    const d = j?.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d) && d.length > 0) {
      const first = d[0] as { msg?: string };
      if (typeof first?.msg === "string") return first.msg;
    }
  } catch {
    /* not JSON */
  }
  if (trimmed.length > 220) return `${trimmed.slice(0, 220)}…`;
  return trimmed;
}

function throwApiError(res: Response, text: string): never {
  throw new ApiError(res.status, formatApiErrorMessage(res.status, text));
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${apiBaseUrl}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throwApiError(res, text);
  }
  return res.json() as Promise<T>;
}

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBaseUrl}${path}`, {
    cache: "no-store",
    headers: {
      ...authHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throwApiError(res, text);
  }
  return res.json() as Promise<T>;
}

export async function patchJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${apiBaseUrl}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throwApiError(res, text);
  }
  return res.json() as Promise<T>;
}
