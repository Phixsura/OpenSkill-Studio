"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Pack {
  id: string;
  name: string;
  slug: string;
  summary: string;
  status: string;
  visibility: string;
  install_count: number;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

const VISIBILITY_COLORS: Record<string, string> = {
  private: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  public: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  unlisted: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
};

export default function PackListPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const perPage = 20;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["packs", orgId, statusFilter, page],
    queryFn: () => {
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      params.set("page", String(page));
      params.set("per_page", String(perPage));
      return apiWithAuth<{ data: Pack[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/packs?${params.toString()}`,
      );
    },
  });

  const packs = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  // Reset page when filter changes
  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {isError && (
        <p className="mb-4 text-sm text-red-600">
          Failed to load skill packs. Please try again.
        </p>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Skill Packs</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Curated bundles of skills and project templates.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/packs/new`}>
          <Button size="sm">New Pack</Button>
        </Link>
      </div>

      <div className="flex gap-3">
        <label htmlFor="status-filter" className="sr-only">Filter by status</label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => handleFilterChange(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="">All</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && packs.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No skill packs found.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {packs.map((pack) => (
          <Link
            key={pack.id}
            href={`/dashboard/orgs/${orgId}/packs/${pack.id}`}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">
                {pack.name}
              </h3>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[pack.status] ?? ""}`}
              >
                {pack.status}
              </span>
            </div>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {pack.summary}
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${VISIBILITY_COLORS[pack.visibility] ?? ""}`}
              >
                {pack.visibility}
              </span>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                {pack.install_count} install{pack.install_count !== 1 ? "s" : ""}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {total > 0 && (
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
