"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Profile {
  id: string;
  context_type: string;
  raw_request: string | null;
  structured_requirements: { goal?: string };
  status: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  confirmed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
};

const CONTEXT_COLORS: Record<string, string> = {
  learning: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  production: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  commercial_project: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  talent_matching: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
};

export default function RequirementsListPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["requirement-profiles", orgId, page],
    queryFn: () =>
      apiWithAuth<{ data: Profile[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/requirement-profiles?page=${page}&per_page=20`,
      ),
  });

  const profiles = data?.data ?? [];
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <div className="space-y-6">
      {isError && (
        <p className="text-sm text-red-600">Failed to load requirement profiles.</p>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Requirements</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Structured learning and production needs — the input to matching.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/requirements/new`}>
          <Button size="sm">New Requirement</Button>
        </Link>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && profiles.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No requirement profiles yet.
        </div>
      )}

      <div className="space-y-3">
        {profiles.map((p) => (
          <Link
            key={p.id}
            href={`/dashboard/orgs/${orgId}/requirements/${p.id}`}
            className="block rounded-lg border p-4 transition-shadow hover:shadow-md"
          >
            <div className="flex items-center gap-2">
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${CONTEXT_COLORS[p.context_type] ?? ""}`}
              >
                {p.context_type.replace("_", " ")}
              </span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[p.status] ?? ""}`}
              >
                {p.status}
              </span>
              <span className="ml-auto text-xs text-[hsl(var(--muted-foreground))]">
                {new Date(p.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="mt-2 truncate text-sm">
              {p.structured_requirements?.goal ??
                p.raw_request ??
                "(no goal specified)"}
            </p>
          </Link>
        ))}
      </div>

      {(page > 1 || hasMore) && (
        <div className="flex items-center justify-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Page {page}</span>
          <Button
            variant="secondary"
            size="sm"
            disabled={!hasMore}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
