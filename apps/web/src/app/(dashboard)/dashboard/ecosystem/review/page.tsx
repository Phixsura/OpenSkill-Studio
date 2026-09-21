"use client";
/** Blind benchmark review — model identity hidden until reveal (Part F). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState } from "../components";

interface Assignment {
  review_id: string;
  alias_label: string;
  output_assets: { kind?: string; ref?: string }[];
  input_snapshot: { prompt?: string };
  submitted: boolean;
  scores: Record<string, number>;
}

const DIMENSIONS = ["quality", "brief_adherence", "consistency", "commercial_readiness"];

export default function BlindReviewPage() {
  const queryClient = useQueryClient();
  const [batchId, setBatchId] = useState("");
  const [activeBatch, setActiveBatch] = useState<string | null>(null);
  const [scores, setScores] = useState<Record<string, Record<string, number>>>({});
  const [error, setError] = useState<string | null>(null);

  const assignments = useQuery({
    queryKey: ["eco-review-assignments", activeBatch],
    enabled: Boolean(activeBatch),
    queryFn: () =>
      apiWithAuth<{ data: Assignment[] }>(
        `/ecosystem/benchmark/review-batches/${activeBatch}/assignments`,
      ),
  });

  const submit = useMutation({
    mutationFn: (reviewId: string) =>
      apiWithAuth(`/ecosystem/benchmark/reviews/${reviewId}/submit`, {
        method: "POST",
        body: JSON.stringify({ scores: scores[reviewId] ?? {} }),
      }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["eco-review-assignments"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Submit failed"),
  });

  const setScore = (reviewId: string, dim: string, value: number) =>
    setScores((s) => ({ ...s, [reviewId]: { ...(s[reviewId] ?? {}), [dim]: value } }));

  const rows = assignments.data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Blind Review</h1>
      <EcosystemNav />
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Model and provider identity stay hidden behind alias labels until every reviewer in the
        batch has submitted.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setActiveBatch(batchId.trim() || null);
        }}
        className="flex gap-2"
      >
        <input
          placeholder="Review batch ID"
          value={batchId}
          onChange={(e) => setBatchId(e.target.value)}
          className="w-80 rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        />
        <button
          type="submit"
          className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))]"
        >
          Load assignments
        </button>
      </form>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {!activeBatch ? (
        <EmptyState icon="🫣" text="Enter the review batch ID you were assigned." />
      ) : assignments.isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading assignments…</div>
      ) : rows.length === 0 ? (
        <EmptyState icon="🫥" text="No assignments found for you in this batch." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {rows.map((a) => (
            <div
              key={a.review_id}
              className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold">{a.alias_label}</span>
                {a.submitted && (
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
                    submitted
                  </span>
                )}
              </div>
              <div className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                Prompt: {a.input_snapshot?.prompt ?? "—"}
              </div>
              <div className="mt-2 font-mono text-xs">
                {a.output_assets.map((asset, i) => (
                  <div key={i}>{asset.ref}</div>
                ))}
              </div>
              {!a.submitted && (
                <div className="mt-3 space-y-2">
                  {DIMENSIONS.map((dim) => (
                    <label key={dim} className="flex items-center justify-between gap-2 text-xs">
                      {dim.replaceAll("_", " ")}
                      <input
                        type="number"
                        min={0}
                        max={5}
                        step={0.5}
                        value={scores[a.review_id]?.[dim] ?? ""}
                        onChange={(e) => setScore(a.review_id, dim, Number(e.target.value))}
                        className="w-20 rounded-md border bg-[hsl(var(--background))] px-2 py-1"
                      />
                    </label>
                  ))}
                  <button
                    onClick={() => submit.mutate(a.review_id)}
                    disabled={submit.isPending}
                    className="mt-2 w-full rounded-md bg-[hsl(var(--primary))] px-3 py-1.5 text-xs text-[hsl(var(--primary-foreground))]"
                  >
                    Submit scores
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
