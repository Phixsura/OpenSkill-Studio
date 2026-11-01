"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { apiWithAuth } from "@/lib/api";

interface ReviewRequest {
  id: string;
  review_type: string;
  status: string;
  title: string;
  target_type: string;
  requested_by: string;
  assigned_to: string | null;
  due_at: string | null;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  in_review: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  returned: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expired: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
  cancelled: "bg-gray-300 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function ReviewsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();

  const status = searchParams.get("status") || "";
  const page = Number(searchParams.get("page") || "1");

  const params = new URLSearchParams({ page: String(page), per_page: "20" });
  if (status) params.set("status", status);

  const { data, isLoading } = useQuery({
    queryKey: ["trust-reviews", orgId, status, page],
    queryFn: () =>
      apiWithAuth<{ data: ReviewRequest[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/reviews?${params}`,
      ),
  });

  const reviews = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Review Queue</h1>

      {/* Filter */}
      <select
        value={status}
        onChange={(e) => {
          const p = new URLSearchParams(searchParams);
          if (e.target.value) p.set("status", e.target.value);
          else p.delete("status");
          p.set("page", "1");
          router.push(`/dashboard/orgs/${orgId}/trust/reviews?${p}`);
        }}
        className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
      >
        <option value="">All Statuses</option>
        {["pending", "in_review", "approved", "rejected", "returned", "expired", "cancelled"].map(
          (s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>,
        )}
      </select>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && reviews.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No review requests found.
        </div>
      )}

      {reviews.length > 0 && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Title</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Target</th>
                  <th className="px-4 py-2 font-medium">Due</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((r) => (
                  <tr key={r.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-medium">{r.title}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                      {r.review_type.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-2">
                      <Badge label={r.status} colors={STATUS_COLORS[r.status] || ""} />
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {r.target_type.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                      {r.due_at ? new Date(r.due_at).toLocaleDateString() : "—"}
                    </td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{total} review{total !== 1 ? "s" : ""}</p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  p.set("page", String(page - 1));
                  router.push(`/dashboard/orgs/${orgId}/trust/reviews?${p}`);
                }}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                disabled={!hasMore}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  p.set("page", String(page + 1));
                  router.push(`/dashboard/orgs/${orgId}/trust/reviews?${p}`);
                }}
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
