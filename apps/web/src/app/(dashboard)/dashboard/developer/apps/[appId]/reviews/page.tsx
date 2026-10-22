"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppVersion {
  id: string;
  version: string;
  review_status: string;
}

interface AppReview {
  id: string;
  app_id: string;
  app_version_id: string;
  submitted_by: string;
  review_status: string;
  reviewer_id: string | null;
  review_notes: string | null;
  automated_checks: {
    checks_passed?: boolean;
    manifest_valid?: boolean;
    permissions_declared?: boolean;
    content_hash_present?: boolean;
  } | null;
  submitted_at: string;
  reviewed_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function AppReviewsPage() {
  const { appId } = useParams<{ appId: string }>();
  const queryClient = useQueryClient();

  const { data: reviewsData, isLoading } = useQuery({
    queryKey: ["app-reviews", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppReview[]; meta: { total: number } }>(
        `/developer/apps/${appId}/reviews`,
      ),
  });

  const { data: versionsData } = useQuery({
    queryKey: ["app-versions", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppVersion[] }>(`/developer/apps/${appId}/versions`),
  });

  const submitMutation = useMutation({
    mutationFn: (versionId: string) =>
      apiWithAuth(`/developer/apps/${appId}/reviews`, {
        method: "POST",
        body: JSON.stringify({ app_version_id: versionId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["app-reviews", appId] });
    },
  });

  const reviews = reviewsData?.data ?? [];
  const versions = versionsData?.data ?? [];
  const unreviewedVersions = versions.filter(
    (v) => v.review_status === "pending" && !reviews.some((r) => r.app_version_id === v.id),
  );

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">Reviews</h1>

      {/* Submit for review */}
      {unreviewedVersions.length > 0 && (
        <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
          <h3 className="mb-2 font-medium">Submit a Version for Review</h3>
          <div className="flex flex-wrap gap-2">
            {unreviewedVersions.map((v) => (
              <Button
                key={v.id}
                size="sm"
                onClick={() => submitMutation.mutate(v.id)}
                disabled={submitMutation.isPending}
              >
                Submit v{v.version}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Review history */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : reviews.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          <p className="text-lg">No reviews yet</p>
          <p className="mt-1 text-sm">Submit a version for platform review to get started</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="rounded-lg border p-5 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span
                    className={`rounded px-2.5 py-0.5 text-sm font-medium ${STATUS_COLORS[review.review_status] ?? ""}`}
                  >
                    {review.review_status}
                  </span>
                  <span className="text-sm text-gray-500">
                    Version: {review.app_version_id.slice(0, 10)}…
                  </span>
                </div>
                <span className="text-sm text-gray-400">
                  {new Date(review.submitted_at).toLocaleDateString()}
                </span>
              </div>

              {/* Automated checks */}
              {review.automated_checks && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {Object.entries(review.automated_checks).map(([key, val]) => (
                    <span
                      key={key}
                      className={`rounded px-2 py-0.5 text-xs ${
                        val
                          ? "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                          : "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                      }`}
                    >
                      {val ? "✓" : "✗"} {key.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              )}

              {/* Review notes */}
              {review.review_notes && (
                <div className="mt-3 rounded bg-gray-50 p-3 text-sm dark:bg-gray-800">
                  <span className="font-medium">Reviewer notes:</span>{" "}
                  {review.review_notes}
                </div>
              )}

              {review.reviewed_at && (
                <p className="mt-2 text-xs text-gray-400">
                  Reviewed: {new Date(review.reviewed_at).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
