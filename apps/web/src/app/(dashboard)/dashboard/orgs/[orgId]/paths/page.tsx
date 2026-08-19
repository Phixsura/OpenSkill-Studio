"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Path {
  id: string;
  name: string;
  slug: string;
  description: string;
  status: string;
  estimated_minutes: number;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

export default function PathsListPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["paths", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Path[]; meta: { total: number } }>(
        `/orgs/${orgId}/paths`,
      ),
  });

  const paths = data?.data ?? [];

  return (
    <div className="space-y-6">
      {isError && (
        <p className="mb-4 text-sm text-red-600">
          Failed to load learning paths. Please try again.
        </p>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Learning Paths</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Create and manage structured learning journeys.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/paths/new`}>
          <Button size="sm">New Path</Button>
        </Link>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Loading...
        </p>
      )}

      {!isLoading && paths.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No learning paths yet.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {paths.map((path) => (
          <Link
            key={path.id}
            href={`/dashboard/orgs/${orgId}/paths/${path.id}`}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">
                {path.name}
              </h3>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[path.status] ?? ""}`}
              >
                {path.status}
              </span>
            </div>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {path.description}
            </p>
            <div className="mt-3 text-xs text-[hsl(var(--muted-foreground))]">
              {path.estimated_minutes > 0
                ? `${path.estimated_minutes} min`
                : "No estimate"}
            </div>
          </Link>
        ))}
      </div>

      {data?.meta && paths.length < data.meta.total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {paths.length} of {data.meta.total} paths
        </p>
      )}
    </div>
  );
}
