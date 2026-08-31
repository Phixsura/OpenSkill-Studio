"use client";

import { useEffect, useRef } from "react";

import { sharedRefresh } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

/**
 * On mount, attempts to refresh the access token from the httpOnly cookie.
 * This restores the session after a full page reload.
 *
 * Uses the SHARED deduplicated refresh from lib/api — refresh tokens rotate
 * on use, so a raw fetch here racing apiWithAuth's 401-refresh would present
 * a just-revoked token and wrongly log the user out.
 */
export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current || isAuthenticated) return;
    initialized.current = true;

    sharedRefresh().catch(() => {
      // No valid session — user stays unauthenticated
    });
  }, [isAuthenticated]);

  return <>{children}</>;
}
