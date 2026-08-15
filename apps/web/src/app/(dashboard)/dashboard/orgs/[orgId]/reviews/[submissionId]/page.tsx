"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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
  note: string | null;
}

interface SubmissionDetail {
  id: string;
  project_id: string;
  version: number;
  status: string;
  is_late: boolean;
  items: SubItem[];
  reviews: { id: string; status: string; score: number | null; feedback: string | null; created_at: string }[];
}

export default function ReviewDetailPage() {
  const { orgId, submissionId } = useParams<{ orgId: string; submissionId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  // We need to find the project_id — fetch the submission directly
  const { data, isLoading, isError } = useQuery({
    queryKey: ["review-submission", submissionId],
    queryFn: async () => {
      // The submission endpoint requires project_id, so we search pending first
      const pending = await apiWithAuth<{ data: { id: string; project_id: string }[] }>(
        `/orgs/${orgId}/reviews/pending`,
      );
      const sub = pending.data.find((s) => s.id === submissionId);
      if (!sub) return null;
      return apiWithAuth<{ data: SubmissionDetail }>(
        `/orgs/${orgId}/projects/${sub.project_id}/submissions/${submissionId}`,
      );
    },
  });

  const sub = data?.data;
  const [score, setScore] = useState("");
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState<string | null>(null);

  const reviewMutation = useMutation({
    mutationFn: (status: string) =>
      apiWithAuth(`/orgs/${orgId}/submissions/${submissionId}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          status,
          score: score ? parseInt(score) : undefined,
          feedback: feedback || undefined,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-reviews"] });
      router.push(`/dashboard/orgs/${orgId}/reviews`);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Review failed"),
  });

  if (isLoading) return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError || !sub) return <p className="text-[hsl(var(--destructive))]">Submission not found.</p>;

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Review Submission v{sub.version}</h1>
        {sub.is_late && <span className="text-sm text-yellow-600">Late submission</span>}
      </div>

      {/* Submitted items — grouped by deliverable, latest version first */}
      <div>
        <h2 className="text-lg font-semibold">Deliverables</h2>
        <div className="mt-3 space-y-3">
          {Object.entries(
            (sub.items ?? []).reduce<Record<string, SubItem[]>>((acc, item) => {
              (acc[item.deliverable_id] ??= []).push(item);
              return acc;
            }, {}),
          ).map(([deliverableId, items]) => {
            const sorted = [...items].sort((a, b) => b.version - a.version);
            const latest = sorted[0];
            if (!latest) return null;
            const history = sorted.slice(1);
            return (
              <div key={deliverableId} className="rounded-lg border p-4">
                <div className="flex items-center gap-2 text-sm">
                  {latest.file_name && <span className="font-medium">{latest.file_name}</span>}
                  {latest.version > 1 && (
                    <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-200">
                      v{latest.version}
                    </span>
                  )}
                  {latest.note && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      📝 {latest.note}
                    </span>
                  )}
                </div>

                <div className="mt-2">
                  {latest.type === "prompt" ? (
                    <PromptDisplay content={latest.content} />
                  ) : latest.type === "file" ? (
                    <div className="space-y-2">
                      <MediaPreview
                        downloadPath={`/orgs/${orgId}/submissions/${submissionId}/files/${latest.id}/download`}
                        mimeType={latest.mime_type}
                        fileName={latest.file_name}
                      />
                      {(() => {
                        const gen = parseGenerationMeta(latest.content);
                        return gen ? <GenerationData meta={gen} /> : null;
                      })()}
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap text-sm">{latest.content}</p>
                  )}
                </div>

                {history.length > 0 && (
                  <details className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                    <summary className="cursor-pointer">
                      Previous versions ({history.length})
                    </summary>
                    <ul className="mt-1 space-y-0.5 pl-4">
                      {history.map((h) => (
                        <li key={h.id}>
                          v{h.version} — {h.file_name ?? h.type}
                          {h.note ? ` (${h.note})` : ""}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Review form */}
      <div className="rounded-lg border p-6 space-y-4">
        <h2 className="text-lg font-semibold">Your Review</h2>

        <div>
          <label className="block text-sm font-medium">Score</label>
          <input
            type="number"
            value={score}
            onChange={(e) => setScore(e.target.value)}
            className="mt-1 block w-32 rounded-md border bg-transparent px-3 py-2 text-sm"
            placeholder="0-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Feedback</label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={5}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            placeholder="Provide constructive feedback..."
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex gap-3">
          <Button
            onClick={() => reviewMutation.mutate("approved")}
            disabled={reviewMutation.isPending}
          >
            ✅ Approve
          </Button>
          <Button
            variant="secondary"
            onClick={() => reviewMutation.mutate("revision_requested")}
            disabled={reviewMutation.isPending}
          >
            ✏️ Request Revision
          </Button>
          <Button
            variant="ghost"
            onClick={() => reviewMutation.mutate("rejected")}
            disabled={reviewMutation.isPending}
          >
            ❌ Reject
          </Button>
        </div>
      </div>

      {/* Previous reviews */}
      {(sub.reviews ?? []).length > 0 && (
        <div>
          <h2 className="text-lg font-semibold">Previous Reviews</h2>
          <div className="mt-3 space-y-3">
            {(sub.reviews ?? []).map((r) => (
              <div key={r.id} className="rounded-lg border p-4 text-sm">
                <div className="flex justify-between">
                  <span className="capitalize">{r.status.replace("_", " ")}</span>
                  {r.score !== null && <span className="font-bold">{r.score} pts</span>}
                </div>
                {r.feedback && <p className="mt-2 text-[hsl(var(--muted-foreground))]">{r.feedback}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
