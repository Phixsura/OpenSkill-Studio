"use client";

import { useParams, useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface Policy {
  id: string;
  name: string;
  version: number;
  is_active: boolean;
  dimensions: {
    key: string;
    label: string;
    description: string;
    weight: number;
    scale_min: number;
    scale_max: number;
    guidance: string;
  }[];
  tier_thresholds: Record<string, { max_score?: number; min_score?: number }>;
}

const RISK_COLORS: Record<string, string> = {
  minimal: "text-green-700 dark:text-green-400",
  low: "text-blue-700 dark:text-blue-400",
  medium: "text-yellow-700 dark:text-yellow-400",
  high: "text-orange-700 dark:text-orange-400",
  critical: "text-red-700 dark:text-red-400",
};

function computePreview(
  scores: Record<string, number>,
  dimensions: Policy["dimensions"],
  thresholds: Policy["tier_thresholds"],
) {
  let totalWeight = 0;
  let weightedSum = 0;
  for (const dim of dimensions) {
    const score = scores[dim.key] ?? 0;
    weightedSum += score * dim.weight;
    totalWeight += dim.weight;
  }
  if (totalWeight === 0) return { score: 0, tier: "—" };
  const score = weightedSum / totalWeight;
  const rounded = Math.round(score * 100) / 100;

  let tier = "critical";
  for (const t of ["minimal", "low", "medium", "high"] as const) {
    const max = thresholds[t]?.max_score;
    if (max !== undefined && rounded <= max) {
      tier = t;
      break;
    }
  }
  return { score: rounded, tier };
}

export default function NewAssessmentPage() {
  const { orgId, systemId } = useParams<{ orgId: string; systemId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const submitting = useRef(false);

  const [scores, setScores] = useState<Record<string, number>>({});
  const [error, setError] = useState("");

  const { data: policiesData, isLoading } = useQuery({
    queryKey: ["trust-policies", orgId],
    queryFn: () => apiWithAuth<{ data: Policy[] }>(`/orgs/${orgId}/trust/risk-policies`),
  });

  const policies = policiesData?.data ?? [];
  const activePolicy = policies.find((p) => p.is_active) ?? policies[0];

  const mutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/trust/systems/${systemId}/assessments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dimension_scores: scores,
          policy_id: activePolicy?.id,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trust-assessments"] });
      router.replace(`/dashboard/orgs/${orgId}/trust/systems/${systemId}`);
    },
    onError: (err: Error) => {
      setError(err?.message || "Failed to create assessment");
      submitting.current = false;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError("");
    mutation.mutate();
  };

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading policy...</p>;
  }

  if (!activePolicy) {
    return <p className="text-sm text-red-600">No risk scoring policy found.</p>;
  }

  const preview = computePreview(scores, activePolicy.dimensions, activePolicy.tier_thresholds);
  const allScored = activePolicy.dimensions.every((d) => scores[d.key] !== undefined);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">New Risk Assessment</h1>
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Scoring with policy: <strong>{activePolicy.name}</strong> (v{activePolicy.version})
      </p>

      {error && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </p>
      )}

      {/* Live Score Preview */}
      <div className="rounded-lg border p-4 text-center">
        <p className="text-xs text-[hsl(var(--muted-foreground))]">Weighted Score Preview</p>
        <p className="mt-1 text-3xl font-bold">{allScored ? preview.score.toFixed(2) : "—"}</p>
        <p className={`mt-1 text-sm font-medium ${RISK_COLORS[preview.tier] || ""}`}>
          {allScored ? preview.tier.replace(/_/g, " ") : "Score all dimensions"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activePolicy.dimensions.map((dim) => (
          <div key={dim.key} className="rounded-lg border p-4">
            <div className="flex items-baseline justify-between">
              <label className="text-sm font-medium">{dim.label}</label>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                weight: {dim.weight}
              </span>
            </div>
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">{dim.description}</p>
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))] italic">{dim.guidance}</p>
            <div className="mt-3 flex items-center gap-3">
              <input
                type="range"
                min={dim.scale_min}
                max={dim.scale_max}
                step={1}
                value={scores[dim.key] ?? dim.scale_min}
                onChange={(e) =>
                  setScores((prev) => ({ ...prev, [dim.key]: Number(e.target.value) }))
                }
                className="flex-1"
              />
              <span className="w-8 text-center text-lg font-bold">
                {scores[dim.key] ?? "—"}
              </span>
            </div>
          </div>
        ))}

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={!allScored || mutation.isPending}
            className="rounded-md bg-[hsl(var(--primary))] px-6 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
          >
            {mutation.isPending ? "Creating..." : "Create Assessment"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border px-6 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
