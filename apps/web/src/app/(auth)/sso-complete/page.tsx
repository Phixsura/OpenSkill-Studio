"use client";

// R69 (ADR-018): SSO landing — the SAML ACS / OIDC callback redirects here
// with tokens in the URL FRAGMENT (never sent to any server, never logged).
// We consume the fragment, hydrate the auth store from /auth/me, scrub the
// hash and continue to the dashboard.

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import { type AuthUser, useAuthStore } from "@/stores/auth";

export default function SsoCompletePage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [error, setError] = useState<string | null>(null);
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return; // StrictMode double-invoke guard
    ran.current = true;
    const params = new URLSearchParams(window.location.hash.slice(1));
    const accessToken = params.get("access_token");
    if (!accessToken) {
      setError("Sign-in response was incomplete. Please try again.");
      return;
    }
    // Scrub the tokens from the address bar / history immediately.
    window.history.replaceState(null, "", window.location.pathname);
    (async () => {
      try {
        const me = await api<{ data: AuthUser }>("/auth/me", {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        setAuth(accessToken, me.data);
        router.replace("/dashboard");
      } catch {
        setError("Could not complete sign-in. Please try again.");
      }
    })();
  }, [router, setAuth]);

  return (
    <div className="text-center">
      <h1 className="text-2xl font-bold tracking-tight">
        {error ? "Sign-in failed" : "Signing you in…"}
      </h1>
      {error && (
        <p role="alert" className="mt-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
