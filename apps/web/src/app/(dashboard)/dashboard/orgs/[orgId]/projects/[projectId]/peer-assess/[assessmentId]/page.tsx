"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { GenerationData, parseGenerationMeta } from "@/components/generation-data";
import { MediaPreview } from "@/components/media-preview";
import { PromptDisplay } from "@/components/prompt-display";
import { apiWithAuth, ApiError } from "@/lib/api";

interface SubItem {
  id: string;
  deliverable_id: string;
  type: string;
  file_name: string | null;
  mime_type: string | null;
  content: string | null;
  version: number;
}

interface ProjectDetail {
  title: string;
  max_score: number;
  rubric: { criterion: string; max_score: number }[];
}

/**
 * Peer assessment page: the reviewer sees the assigned submission's work
 * (anonymously — no author identity is fetched) and scores it against the
 * project rubric.
 */
export default function PeerAssessPage() {
  const { orgId, projectId, assessmentId } = useParams<{
    orgId: string;
    projectId: string;
    assessmentId: string;
  }>();
  const search = useSearchParams();
  const submissionId = search.get("submission");
  const router = useRouter();

  const { data: projectData } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectDetail }>(`/orgs/${orgId}/projects/${projectId}`),
  });
  const project = projectData?.data;

  const { data: subData, isError } = useQuery({
    queryKey: ["peer-sub", submissionId],
    enabled: !!submissionId,
    queryFn: () =>
      apiWithAuth<{ data: { items: SubItem[] } }>(
        `/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}`,
      ),
  });
  const items = subData?.data?.items ?? [];

  const rubric = project?.rubric ?? [];
  const [scores, setScores] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const total = rubric.reduce((acc, r) => {
    const v = parseInt(scores[r.criterion] ?? "", 10);
    return acc + (Number.isNaN(v) ? 0 : Math.min(v, r.max_score));
  }, 0);

  const submit = async () => {
    setError(null);
    for (const r of rubric) {
      const v = parseInt(scores[r.criterion] ?? "", 10);
      if (Number.isNaN(v) || v < 0 || v > r.max_score) {
        setError(`Enter a score between 0 and ${r.max_score} for "${r.criterion}".`);
        return;
      }
    }
    setBusy(true);
    try {
      await apiWithAuth(`/orgs/${orgId}/peer-assessments/${assessmentId}/submit`, {
        method: "POST",
        body: JSON.stringify({
          score: total,
          score_breakdown: rubric.map((r) => ({
            criterion: r.criterion,
            score: parseInt(scores[r.criterion] ?? "0", 10),
            max_score: r.max_score,
          })),
          feedback: feedback.trim() || undefined,
        }),
      });
      router.push(`/dashboard/orgs/${orgId}/projects/${projectId}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to submit assessment");
      setBusy(false);
    }
  };

  // Group items by deliverable, latest version only
  const latestByDeliverable = new Map<string, SubItem>();
  for (const item of items) {
    const prev = latestByDeliverable.get(item.deliverable_id);
    if (!prev || item.version > prev.version) latestByDeliverable.set(item.deliverable_id, item);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Peer Review</h1>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Review this submission against the rubric. Be specific and constructive — feedback is
          how everyone improves.
        </p>
      </div>

      {isError && (
        <p className="text-sm text-[hsl(var(--destructive))]">Could not load the submission.</p>
      )}

      {/* The work under review */}
      <div>
        <h2 className="text-lg font-semibold">Submitted work</h2>
        <div className="mt-3 space-y-3">
          {[...latestByDeliverable.values()].map((item) => (
            <div key={item.id} className="rounded-lg border p-4">
              {item.file_name && (
                <p className="mb-2 text-sm font-medium">{item.file_name}</p>
              )}
              {item.type === "prompt" ? (
                <PromptDisplay content={item.content} />
              ) : item.type === "file" ? (
                <div className="space-y-2">
                  <MediaPreview
                    downloadPath={`/orgs/${orgId}/submissions/${submissionId}/files/${item.id}/download`}
                    mimeType={item.mime_type}
                    fileName={item.file_name}
                  />
                  {(() => {
                    const gen = parseGenerationMeta(item.content);
                    return gen ? <GenerationData meta={gen} /> : null;
                  })()}
                </div>
              ) : (
                <p className="whitespace-pre-wrap text-sm">{item.content}</p>
              )}
            </div>
          ))}
          {items.length === 0 && !isError && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading work…</p>
          )}
        </div>
      </div>

      {/* Rubric scoring */}
      <div className="rounded-lg border p-6">
        <h2 className="text-lg font-semibold">Your assessment</h2>
        <div className="mt-3 space-y-3">
          {rubric.map((r) => (
            <div key={r.criterion} className="flex items-center justify-between gap-4">
              <span className="text-sm">{r.criterion}</span>
              <div className="flex items-center gap-1.5 text-sm">
                <input
                  type="number"
                  min={0}
                  max={r.max_score}
                  className="w-20 rounded-md border bg-transparent px-2 py-1 text-right text-sm"
                  value={scores[r.criterion] ?? ""}
                  onChange={(e) =>
                    setScores((s) => ({ ...s, [r.criterion]: e.target.value }))
                  }
                />
                <span className="text-[hsl(var(--muted-foreground))]">/ {r.max_score}</span>
              </div>
            </div>
          ))}
          <div className="flex items-center justify-between border-t pt-2 text-sm font-medium">
            <span>Total</span>
            <span>
              {total} / {project?.max_score ?? 100}
            </span>
          </div>

          <textarea
            className="block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            rows={4}
            placeholder="What works well? What should improve? Be concrete."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button onClick={submit} disabled={busy}>
            {busy ? "Submitting…" : "Submit review"}
          </Button>
        </div>
      </div>
    </div>
  );
}
