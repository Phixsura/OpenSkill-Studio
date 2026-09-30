"use client";
/**
 * Self-serve experiment hook (ADR-017 §7, client-SDK class).
 *
 * The authenticated user IS the unit: the backend resolves a sticky variant
 * for user.id through the fail-safe facade, so a missing/paused experiment
 * (or any backend error) yields the default experience (`variantKey: null`).
 *
 *   const { variantKey, config, recordExposure } = useExperiment("surface-x");
 *   // render by variantKey; call recordExposure() at the moment the
 *   // variant actually takes effect (assignment ≠ exposure)
 */

import { useCallback } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";

interface ResolveResponse {
  data: {
    variant_key: string | null;
    config: Record<string, unknown>;
    assigned_version?: number;
  };
}

export function useExperiment(experimentKey: string) {
  const resolve = useQuery({
    queryKey: ["experiment-self-resolve", experimentKey],
    staleTime: 5 * 60 * 1000, // sticky server-side; no need to re-ask often
    queryFn: () =>
      apiWithAuth<ResolveResponse>("/experiments/self/resolve", {
        method: "POST",
        body: JSON.stringify({ experiment_key: experimentKey }),
      }),
  });

  const exposure = useMutation({
    mutationFn: (dedupKey?: string) =>
      apiWithAuth("/experiments/self/exposures", {
        method: "POST",
        body: JSON.stringify({
          experiment_key: experimentKey,
          dedup_key: dedupKey ?? null,
        }),
      }),
  });

  const recordExposure = useCallback((dedupKey?: string) => exposure.mutate(dedupKey), [exposure]);

  return {
    variantKey: resolve.data?.data.variant_key ?? null,
    config: resolve.data?.data.config ?? {},
    isLoading: resolve.isLoading,
    recordExposure,
  };
}
