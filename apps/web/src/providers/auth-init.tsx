"use client";

import { useEffect, useRef } from "react";

import { useAuthStore } from "@/stores/auth";

/**
 * On mount, attempts to refresh the access token from the httpOnly cookie.
 * This restores the session after a full page reload.
 */
export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const setAuth = useAuthStore((s) => s.setAuth);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current || isAuthenticated) return;
    initialized.current = true;

    const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

    fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    })
      .then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          setAuth(data.access_token, data.user);
        }
      })
      .catch(() => {
        // No valid session — user stays unauthenticated
      });
  }, [setAuth, isAuthenticated]);

  return <>{children}</>;
}
