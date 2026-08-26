"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api, apiWithAuth } from "@/lib/api";

interface Installation {
  id: string;
  pack_id: string | null;
  installed_version: string;
  status: string;
  locally_modified: boolean;
  installed_at: string;
}

interface PackName {
  id: string;
  name: string;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  forked: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  removed: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function WorkflowInstallationsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [page, setPage] = useState(1);
  const perPage = 20;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-installations", orgId, page],
    queryFn: () =>
      apiWithAuth<{ data: Installation[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/workflow-installations?page=${page}&per_page=${perPage}`,
      ),
  });

  const installations = data?.data ?? [];
  const total = data?.meta?.total ?? 0;
  const hasMore = data?.meta?.has_more ?? false;

  // The installation response carries only pack_id — resolve display names
  // via the public registry (mirrors the detail page). Private packs 404
  // there; fail silently per pack and fall back to the ULID.
  const packIds = [...new Set(installations.flatMap((i) => (i.pack_id ? [i.pack_id] : [])))];
  const { data: packNamesData } = useQuery({
    queryKey: ["registry-workflow-pack-names", packIds],
    enabled: packIds.length > 0,
    queryFn: async () => {
      const results = await Promise.all(
        packIds.map((id) =>
          api<{ data: PackName }>(`/registry/workflow-packs/${id}`).catch(() => null),
        ),
      );
      return Object.fromEntries(
        results.flatMap((r) => (r ? [[r.data.id, r.data.name]] : [])),
      ) as Record<string, string>;
    },
  });
  const packNames = packNamesData ?? {};

  return (
    <div className="space-y-6">
      {isError && (
        <p className="text-sm text-red-600">Failed to load workflow installations.</p>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflow Installations</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Workflow packs installed in this organization.
          </p>
        </div>
        <Link href="/registry/workflows">
          <Button size="sm" variant="secondary">Browse Registry</Button>
        </Link>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && installations.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No workflow packs installed yet.
        </div>
      )}

      <div className="space-y-3">
        {installations.map((install) => (
          <Link
            key={install.id}
            href={`/dashboard/orgs/${orgId}/workflow-installations/${install.id}`}
            className="flex items-center justify-between rounded-lg border p-4 transition-shadow hover:shadow-md"
          >
            <div>
              <p className="font-medium">
                {(install.pack_id ? packNames[install.pack_id] : null) ??
                  install.pack_id ??
                  "(pack removed)"}
              </p>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                v{install.installed_version} · installed{" "}
                {new Date(install.installed_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {install.locally_modified && (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                  modified
                </span>
              )}
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[install.status] ?? ""}`}
              >
                {install.status}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {(total > perPage || page > 1) && (
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
