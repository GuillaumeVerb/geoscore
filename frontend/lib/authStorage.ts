/** Minimal client session: JWT + user summary (no refresh token). */

const TOKEN_KEY = "geoscore_access_token";
const USER_KEY = "geoscore_user";

export type StoredUser = { id: string; email: string };

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): StoredUser | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredUser;
  } catch {
    return null;
  }
}

export function isSignedIn(): boolean {
  return Boolean(getAuthToken());
}

export function setAuthSession(token: string, user: StoredUser) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
  window.dispatchEvent(new Event("geoscore-auth"));
}

export function clearAuthSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  window.dispatchEvent(new Event("geoscore-auth"));
}
