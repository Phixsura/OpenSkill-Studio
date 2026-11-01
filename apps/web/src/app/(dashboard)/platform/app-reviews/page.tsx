"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppReview {
  id: string;
  app_id: string;
  app_version_id: string;
  submitted_by: string;
  review_status: string;
  reviewer_id: string | null;
  review_notes: string | null;
  automated_checks: Record<string, unknown> | null;
  submitted_at: string;
  reviewed_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function AppReviewQueuePage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("pending");
  const [selectedReview, setSelectedReview] = useState<AppReview | null>(null);
  const [notes, setNotes] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-app-reviews", statusFilter],
    queryFn: () =>
      apiWithAuth<{ data: AppReview[]; meta: { total: number } }>(
        `/admin/app-reviews?status=${statusFilter}`,
      ),
  });

  const decideMutation = useMutation({
    mutationFn: ({ reviewId, decision }: { reviewId: string; decision: string }) =>
      apiWithAuth(`/admin/app-reviews/${reviewId}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision, notes: notes || undefined }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-app-reviews"] });
      setSelectedReview(null);
      setNotes("");
    },
  });

  const reviews = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">App Review Queue</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Review and approve third-party app submissions
          </p>
        </div>
        <div className="flex gap-2">
          {["pending", "approved", "rejected"].map((s) => (
            <button
              key={s}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                statusFilter === s
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              }`}
              onClick={() => setStatusFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <p className="mb-4 text-sm text-gray-400">{total} review(s)</p>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : reviews.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          No {statusFilter} reviews
        </div>
      ) : (
        <div className="space-y-3">
          {reviews.map((review) => (
            <div
              key={review.id}
              className={`cursor-pointer rounded-lg border p-4 transition-colors dark:border-gray-700 ${
                selectedReview?.id === review.id
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "hover:border-gray-400"
              }`}
              onClick={() => setSelectedReview(review)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium">App: {review.app_id.slice(0, 12)}…</span>
                  <span className="ml-2 text-sm text-gray-500">
                    Version: {review.app_version_id.slice(0, 12)}…
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[review.review_status] ?? ""}`}
                  >
                    {review.review_status}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(review.submitted_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Automated checks summary */}
              {review.automated_checks && (
                <div className="mt-2 flex gap-2 text-xs">
                  {review.automated_checks.checks_passed ? (
                    <span className="text-green-600">✅ Automated checks passed</span>
                  ) : (
                    <span className="text-red-600">❌ Automated checks failed</span>
                  )}
                </div>
              )}

              {review.review_notes && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Notes: {review.review_notes}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Review Decision Panel */}
      {selectedReview && selectedReview.review_status === "pending" && (
        <div className="mt-6 rounded-lg border p-6 dark:border-gray-700">
          <h3 className="mb-4 font-semibold">Review Decision</h3>
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium">Notes (optional)</label>
            <textarea
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Feedback for the developer..."
            />
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() =>
                decideMutation.mutate({
                  reviewId: selectedReview.id,
                  decision: "approved",
                })
              }
              disabled={decideMutation.isPending}
            >
              ✅ Approve
            </Button>
            <Button
              variant="destructive"
              onClick={() =>
                decideMutation.mutate({
                  reviewId: selectedReview.id,
                  decision: "rejected",
                })
              }
              disabled={decideMutation.isPending}
            >
              ❌ Reject
            </Button>
            <Button variant="outline" onClick={() => setSelectedReview(null)}>
              Cancel
            </Button>
          </div>
          {decideMutation.isError && (
            <p className="mt-2 text-sm text-red-600">
              {(decideMutation.error as Error).message}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
