"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Installation {
  id: string;
  pack_id: string | null;
  pack_name?: string | null;
  installed_version: string;
  status: string;
  locally_modified: boolean;
  installed_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  forked: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  removed: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function WorkflowInstallationsPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-installations", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Installation[] }>(`/orgs/${orgId}/workflow-installations`),
  });

  const installations = data?.data ?? [];

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
                {install.pack_name ?? install.pack_id ?? "(pack removed)"}
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
    </div>
  );
}
