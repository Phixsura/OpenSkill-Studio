"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { apiWithAuth } from "@/lib/api";

interface Run {
  id: string;
  pack_id: string | null;
  status: string;
  error_code: string | null;
  created_at: string;
  finished_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  waiting_review: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

const NON_TERMINAL = new Set(["pending", "running", "waiting_review"]);

export default function WorkflowRunsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [page, setPage] = useState(1);
  const perPage = 20;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-runs", orgId, page],
    queryFn: () =>
      apiWithAuth<{ data: Run[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/workflow-runs?page=${page}&per_page=${perPage}`,
      ),
    refetchInterval: (query) => {
      const runs = query.state.data?.data ?? [];
      return runs.some((r) => NON_TERMINAL.has(r.status)) ? 5000 : false;
    },
  });

  const runs = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      {isError && <p className="text-sm text-red-600">Failed to load workflow runs.</p>}
      <div>
        <h1 className="text-3xl font-bold">Workflow Runs</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Execution history for installed workflows.
        </p>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && runs.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No workflow runs yet. Start one from an installation.
        </div>
      )}

      <div className="space-y-2">
        {runs.map((run) => (
          <Link
            key={run.id}
            href={`/dashboard/orgs/${orgId}/workflow-runs/${run.id}`}
            className="flex items-center justify-between rounded-lg border px-4 py-3 transition-shadow hover:shadow-md"
          >
            <div>
              <p className="font-mono text-sm">{run.id}</p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {new Date(run.created_at).toLocaleString()}
                {run.error_code ? ` · ${run.error_code}` : ""}
              </p>
            </div>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[run.status] ?? ""}`}
            >
              {run.status}
            </span>
          </Link>
        ))}
      </div>

      {total > perPage && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Showing {(page - 1) * perPage + 1}–{Math.min(page * perPage, total)} of {total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasMore}
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
