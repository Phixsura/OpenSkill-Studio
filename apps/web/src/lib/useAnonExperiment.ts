"use client";
/**
 * Pre-login experiment hook (ADR-017 §4.17, round 217).
 *
 * The unit is a device-held anonymous ULID-class id persisted in
 * localStorage; the backend resolves through the same fail-safe facade,
 * so a missing experiment or any error yields the default experience.
 * After login, POST /experiments/self/identity-link with the same id
 * (see claimAnonymousId) carries the whole pre-login history to the
 * user — one person, one experience.
 *
 *   const { variantKey, config, recordExposure } = useAnonExperiment("surface-x");
 */

import { useCallback } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api, apiWithAuth } from "@/lib/api";

const STORAGE_KEY = "osk-anon-id";

/** Crockford-base32 ULID-shaped token, 26 chars, no ':' (the schema wall). */
function generateAnonId(): string {
  const alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
  const bytes = new Uint8Array(26);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => alphabet[b % 32]).join("");
}

export function getAnonymousId(): string | null {
  // localStorage can throw (private windows, blocked site data) — the
  // hook degrades to the default experience rather than crashing the page
  try {
    let id = window.localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = generateAnonId();
      window.localStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    return null;
  }
}

/** Call once after login: claims the device's pre-login id for the user. */
export async function claimAnonymousId(): Promise<boolean> {
  const anonymousId = getAnonymousId();
  if (!anonymousId) return false;
  try {
    await apiWithAuth("/experiments/self/identity-link", {
      method: "POST",
      body: JSON.stringify({ anonymous_id: anonymousId }),
    });
    return true;
  } catch {
    // a 422 here means the id belongs to another user (shared device) —
    // fail-safe: the login experience proceeds, histories stay separate
    return false;
  }
}

interface ResolveResponse {
  data: {
    variant_key: string | null;
    config: Record<string, unknown>;
    assigned_version?: number;
  };
}

export function useAnonExperiment(experimentKey: string) {
  const anonymousId = typeof window === "undefined" ? null : getAnonymousId();

  const resolve = useQuery({
    queryKey: ["experiment-anon-resolve", experimentKey, anonymousId],
    enabled: anonymousId !== null,
    staleTime: 5 * 60 * 1000,
    queryFn: () =>
      api<ResolveResponse>("/experiments/anon/resolve", {
        method: "POST",
        body: JSON.stringify({
          experiment_key: experimentKey,
          anonymous_id: anonymousId,
        }),
      }),
  });

  const exposure = useMutation({
    mutationFn: (dedupKey?: string) =>
      api("/experiments/anon/exposures", {
        method: "POST",
        body: JSON.stringify({
          experiment_key: experimentKey,
          anonymous_id: anonymousId,
          dedup_key: dedupKey ?? null,
        }),
      }),
  });

  // identity-stable callback (the #57 lesson)
  const { mutate: mutateExposure } = exposure;
  const recordExposure = useCallback(
    (dedupKey?: string) => {
      if (anonymousId !== null) mutateExposure(dedupKey);
    },
    [mutateExposure, anonymousId],
  );

  // null-safe fail-safe shape (the #54 lesson)
  const payload = resolve.data?.data ?? null;
  return {
    variantKey: payload?.variant_key ?? null,
    config: payload?.config ?? {},
    isLoading: resolve.isLoading,
    anonymousId,
    recordExposure,
  };
}
