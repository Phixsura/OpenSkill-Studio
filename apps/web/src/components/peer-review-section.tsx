"use client";

import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Round {
  id: string;
  project_id: string;
  name: string;
  num_reviews: number;
  anonymous: boolean;
  include_self_review: boolean;
  phase: "setup" | "assessment" | "closed";
  deadline: string | null;
  created_at: string;
}

interface MyAssessment {
  id: string;
  submission_id: string;
  is_self_review: boolean;
  status: "pending" | "submitted";
  score: number | null;
}

interface ResultEntry {
  submission_id: string;
  avg_score: number | null;
  review_count: number;
}

const PHASE_LABEL: Record<Round["phase"], string> = {
  setup: "Collecting submissions",
  assessment: "Peer review in progress",
  closed: "Closed",
};

/**
 * Peer review block on a project page.
 * Instructors: create rounds, start allocation, close.
 * Learners: see their assigned reviews and jump into assessing.
 */
export function PeerReviewSection({
  orgId,
  projectId,
  isInstructor,
}: {
  orgId: string;
  projectId: string;
  isInstructor: boolean;
}) {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("Peer Review");
  const [numReviews, setNumReviews] = useState("2");
  const [anonymous, setAnonymous] = useState(true);
  const [selfReview, setSelfReview] = useState(false);

  const { data: roundsData } = useQuery({
    queryKey: ["peer-rounds", projectId],
    queryFn: () =>
      apiWithAuth<{ data: Round[] }>(`/orgs/${orgId}/projects/${projectId}/peer-review-rounds`),
  });
  const rounds = roundsData?.data ?? [];
  const activeRound = rounds.find((r) => r.phase !== "closed") ?? rounds[0];

  const { data: myData } = useQuery({
    queryKey: ["peer-my", activeRound?.id],
    enabled: !!activeRound && activeRound.phase === "assessment",
    queryFn: () =>
      apiWithAuth<{ data: MyAssessment[] }>(
        `/orgs/${orgId}/peer-review-rounds/${activeRound!.id}/my-assessments`,
      ),
  });
  const myAssessments = myData?.data ?? [];

  const { data: resultsData } = useQuery({
    queryKey: ["peer-results", activeRound?.id],
    enabled: !!activeRound && activeRound.phase === "closed",
    queryFn: () =>
      apiWithAuth<{ data: ResultEntry[] }>(
        `/orgs/${orgId}/peer-review-rounds/${activeRound!.id}/results`,
      ),
  });
  const results = resultsData?.data ?? [];

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["peer-rounds", projectId] });
    queryClient.invalidateQueries({ queryKey: ["peer-my"] });
    queryClient.invalidateQueries({ queryKey: ["peer-results"] });
  };

  const createRound = async () => {
    setError(null);
    try {
      await apiWithAuth(`/orgs/${orgId}/peer-review-rounds`, {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId,
          name: name.trim() || "Peer Review",
          num_reviews: parseInt(numReviews, 10) || 2,
          anonymous,
          include_self_review: selfReview,
        }),
      });
      setCreating(false);
      invalidate();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create round");
    }
  };

  const transition = async (roundId: string, action: "start" | "close") => {
    setError(null);
    try {
      await apiWithAuth(`/orgs/${orgId}/peer-review-rounds/${roundId}/${action}`, {
        method: "POST",
      });
      invalidate();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : `Failed to ${action} round`);
    }
  };

  if (!isInstructor && rounds.length === 0) return null;

  return (
    <div data-testid="peer-review-section">
      <h2 className="text-xl font-semibold">Peer Review</h2>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}

      {rounds.length === 0 && isInstructor && !creating && (
        <div className="mt-3">
          <Button variant="secondary" size="sm" onClick={() => setCreating(true)}>
            Set up peer review
          </Button>
        </div>
      )}

      {creating && (
        <div className="mt-3 space-y-2 rounded-lg border p-4">
          <Input placeholder="Round name" value={name} onChange={(e) => setName(e.target.value)} />
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <label className="flex items-center gap-1.5">
              Reviews per learner
              <Input
                className="w-16"
                inputMode="numeric"
                value={numReviews}
                onChange={(e) => setNumReviews(e.target.value)}
              />
            </label>
            <label className="flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={anonymous}
                onChange={(e) => setAnonymous(e.target.checked)}
              />
              Anonymous
            </label>
            <label className="flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={selfReview}
                onChange={(e) => setSelfReview(e.target.checked)}
              />
              Include self-review
            </label>
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={createRound}>
              Create round
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setCreating(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {activeRound && (
        <div className="mt-3 rounded-lg border p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span className="font-medium">{activeRound.name}</span>
              <span className="ml-2 rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                {PHASE_LABEL[activeRound.phase]}
              </span>
              {activeRound.anonymous && (
                <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                  🕶 Anonymous
                </span>
              )}
            </div>
            {isInstructor && activeRound.phase === "setup" && (
              <Button size="sm" onClick={() => transition(activeRound.id, "start")}>
                Allocate & start
              </Button>
            )}
            {isInstructor && activeRound.phase === "assessment" && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => transition(activeRound.id, "close")}
              >
                Close round
              </Button>
            )}
          </div>

          {/* Learner queue */}
          {activeRound.phase === "assessment" && myAssessments.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-medium">
                Your reviews (
                {myAssessments.filter((a) => a.status === "submitted").length}/
                {myAssessments.length} done)
              </p>
              <ul className="mt-1.5 space-y-1">
                {myAssessments.map((a, i) => (
                  <li key={a.id} className="flex items-center gap-2 text-sm">
                    {a.status === "submitted" ? (
                      <span className="text-green-600">✓ Reviewed</span>
                    ) : (
                      <Link
                        href={`/dashboard/orgs/${orgId}/projects/${projectId}/peer-assess/${a.id}?submission=${a.submission_id}&round=${activeRound.id}`}
                        className="text-[hsl(var(--primary))] hover:underline"
                      >
                        {a.is_self_review ? "Self-review" : `Review submission ${i + 1}`} →
                      </Link>
                    )}
                    {a.is_self_review && (
                      <span className="rounded-full bg-[hsl(var(--secondary))] px-1.5 py-0.5 text-xs">
                        self
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Results (closed) */}
          {activeRound.phase === "closed" && results.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-medium">Results</p>
              <table className="mt-1.5 w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-[hsl(var(--muted-foreground))]">
                    <th className="py-1">Submission</th>
                    <th className="py-1 text-right">Avg score</th>
                    <th className="py-1 text-right">Reviews</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r) => (
                    <tr key={r.submission_id} className="border-t">
                      <td className="py-1 font-mono text-xs">{r.submission_id.slice(-8)}</td>
                      <td className="py-1 text-right font-medium">{r.avg_score ?? "—"}</td>
                      <td className="py-1 text-right">{r.review_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
