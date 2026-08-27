"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface StepRun {
  id: string;
  step_id: string;
  step_type: string;
  status: string;
  attempt: number;
  max_attempts: number;
  output: Record<string, unknown> | null;
  error_code: string | null;
  error: string | null;
}

interface RunEvent {
  id: string;
  step_id: string | null;
  event_type: string;
  created_at: string;
}

interface RunDetail {
  id: string;
  status: string;
  error_code: string | null;
  error: string | null;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown> | null;
  created_at: string;
  finished_at: string | null;
  step_runs: StepRun[];
  events: RunEvent[];
}

interface StepReview {
  id: string;
  step_run_id: string;
  instructions: string | null;
  due_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  ready: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  waiting_review: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  waiting_retry: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  skipped: "bg-gray-100 text-gray-500 dark:bg-gray-900 dark:text-gray-400",
  cancelled: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

const NON_TERMINAL = new Set(["pending", "running", "waiting_review"]);

export default function WorkflowRunDetailPage() {
  const { orgId, runId } = useParams<{ orgId: string; runId: string }>();
  const queryClient = useQueryClient();
  // Keyed per review id — parallel branches can suspend multiple review
  // gates at once, and a single shared note would leak text across gates.
  const [notes, setNotes] = useState<Record<string, string>>({});

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-run", orgId, runId],
    queryFn: () => apiWithAuth<{ data: RunDetail }>(`/orgs/${orgId}/workflow-runs/${runId}`),
    refetchInterval: (query) =>
      NON_TERMINAL.has(query.state.data?.data.status ?? "") ? 3000 : false,
  });
  const run = data?.data;

  const waitingReview = run?.step_runs.some((s) => s.status === "waiting_review") ?? false;

  const { data: reviewsData } = useQuery({
    queryKey: ["step-reviews", orgId],
    enabled: waitingReview,
    queryFn: () => apiWithAuth<{ data: StepReview[] }>(`/orgs/${orgId}/step-reviews`),
  });

  const decideMutation = useMutation({
    mutationFn: ({ reviewId, decision }: { reviewId: string; decision: string }) =>
      apiWithAuth(`/orgs/${orgId}/step-reviews/${reviewId}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision, note: notes[reviewId] || undefined }),
      }),
    onSuccess: (_data, { reviewId }) => {
      // Clear only the decided review's note — other gates keep theirs
      setNotes((prev) => {
        const next = { ...prev };
        delete next[reviewId];
        return next;
      });
      queryClient.invalidateQueries({ queryKey: ["workflow-run", orgId, runId] });
      queryClient.invalidateQueries({ queryKey: ["step-reviews", orgId] });
      toast.success("Decision recorded");
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Decision failed"),
  });

  const cancelMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-runs/${runId}/cancel`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-run", orgId, runId] });
      toast.success("Run cancelled");
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Cancel failed"),
  });

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !run) {
    return <p className="text-sm text-red-600">Failed to load run.</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-mono text-2xl font-bold">{run.id}</h1>
          <div className="mt-2 flex items-center gap-2">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[run.status] ?? ""}`}
            >
              {run.status}
            </span>
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              started {new Date(run.created_at).toLocaleString()}
            </span>
          </div>
          {run.error && (
            <p className="mt-2 text-sm text-red-600" role="alert">
              {run.error_code}: {run.error}
            </p>
          )}
        </div>
        {NON_TERMINAL.has(run.status) && (
          <Button
            size="sm"
            variant="secondary"
            disabled={cancelMutation.isPending}
            onClick={() => {
              if (window.confirm("Cancel this run?")) cancelMutation.mutate();
            }}
          >
            Cancel Run
          </Button>
        )}
      </div>

      {/* Outputs */}
      {run.outputs && Object.keys(run.outputs).length > 0 && (
        <section>
          <h2 className="text-xl font-semibold">Outputs</h2>
          <pre className="mt-2 overflow-x-auto rounded-lg border bg-[hsl(var(--secondary))] p-4 text-xs">
            {JSON.stringify(run.outputs, null, 2)}
          </pre>
        </section>
      )}

      {/* Step timeline */}
      <section>
        <h2 className="text-xl font-semibold">Steps</h2>
        <ol className="mt-3 space-y-2">
          {run.step_runs.map((step) => {
            const review = reviewsData?.data.find((r) => r.step_run_id === step.id);
            return (
              <li key={step.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono text-sm font-medium">{step.step_id}</span>
                    <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {step.step_type}
                      {step.attempt > 1 ? ` · attempt ${step.attempt}/${step.max_attempts}` : ""}
                    </span>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[step.status] ?? ""}`}
                  >
                    {step.status}
                  </span>
                </div>
                {step.error && (
                  <p className="mt-1 text-xs text-red-600">
                    {step.error_code}: {step.error}
                  </p>
                )}
                {step.output && (
                  <pre className="mt-2 max-h-32 overflow-auto rounded bg-[hsl(var(--secondary))] p-2 text-[10px]">
                    {JSON.stringify(step.output, null, 2).slice(0, 1000)}
                  </pre>
                )}

                {/* Review decision */}
                {step.status === "waiting_review" && review && (
                  <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950">
                    <p className="text-sm font-medium">Review required</p>
                    {review.instructions && <p className="mt-1 text-sm">{review.instructions}</p>}
                    <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                      Due {new Date(review.due_at).toLocaleString()}
                    </p>
                    <textarea
                      value={notes[review.id] ?? ""}
                      onChange={(e) =>
                        setNotes((prev) => ({ ...prev, [review.id]: e.target.value }))
                      }
                      rows={2}
                      maxLength={2000}
                      placeholder="Decision note (optional)"
                      aria-label="Decision note"
                      className="mt-2 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
                    />
                    <div className="mt-2 flex gap-2">
                      <Button
                        size="sm"
                        disabled={decideMutation.isPending}
                        onClick={() =>
                          decideMutation.mutate({ reviewId: review.id, decision: "approved" })
                        }
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={decideMutation.isPending}
                        onClick={() => {
                          // Reject is irreversible: it fails the step and the
                          // whole run (WF_REVIEW_REJECTED), and the decision
                          // row is durable (no re-decide — 409). Confirm before
                          // firing, matching how Cancel Run is guarded on this
                          // same page.
                          if (
                            window.confirm(
                              "Reject this review? This fails the step and cannot be undone — the run will end as failed.",
                            )
                          ) {
                            decideMutation.mutate({ reviewId: review.id, decision: "rejected" });
                          }
                        }}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </section>

      {/* Events */}
      <section>
        <details className="rounded-lg border p-4">
          <summary className="cursor-pointer text-sm font-medium">
            Event log ({run.events.length})
          </summary>
          <ul className="mt-2 space-y-1">
            {run.events.map((event) => (
              <li key={event.id} className="text-xs text-[hsl(var(--muted-foreground))]">
                {new Date(event.created_at).toLocaleTimeString()} — {event.event_type}
                {event.step_id ? ` (${event.step_id})` : ""}
              </li>
            ))}
          </ul>
        </details>
      </section>
    </div>
  );
}
