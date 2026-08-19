"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface InstallDetail {
  id: string;
  org_id: string;
  pack_id: string;
  release_id: string;
  installed_version: string;
  status: string;
  installed_by: string;
  installed_at: string;
  update_available: boolean;
  latest_version?: string;
}

interface DiffItem {
  type: string;
  logical_id: string;
  name: string;
  fields?: Record<string, unknown>;
  reason?: string;
}

interface DiffResult {
  added: DiffItem[];
  changed: DiffItem[];
  removed: DiffItem[];
  conflicts: DiffItem[];
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  forked: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  removed: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

export default function InstallationDetailPage() {
  const { orgId, installId } = useParams<{ orgId: string; installId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submitting = useRef(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["installation", orgId, installId],
    queryFn: () =>
      apiWithAuth<{ data: InstallDetail }>(
        `/orgs/${orgId}/installations/${installId}`,
      ),
  });

  const install = data?.data;

  const handleViewChanges = async () => {
    if (!install?.latest_version) return;
    setLoadingDiff(true);
    setError(null);
    try {
      const res = await apiWithAuth<{ data: DiffResult }>(
        `/orgs/${orgId}/installations/${installId}/diff?version=${install.latest_version}`,
      );
      setDiff(res.data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load diff.");
    } finally {
      setLoadingDiff(false);
    }
  };

  const handleFork = async () => {
    if (submitting.current) return;
    if (!window.confirm("Fork this installation? It will be detached from upstream updates.")) return;
    submitting.current = true;
    setError(null);

    try {
      await apiWithAuth(`/orgs/${orgId}/installations/${installId}/fork`, {
        method: "POST",
      });
      toast.success("Installation forked successfully.");
      queryClient.invalidateQueries({ queryKey: ["installation", orgId, installId] });
      queryClient.invalidateQueries({ queryKey: ["installations", orgId] });
      router.push(`/dashboard/orgs/${orgId}/installations`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to fork installation.");
    } finally {
      submitting.current = false;
    }
  };

  const handleRemove = async () => {
    if (submitting.current) return;
    if (!window.confirm("Remove this installation? This action cannot be undone.")) return;
    submitting.current = true;
    setError(null);

    try {
      await apiWithAuth(`/orgs/${orgId}/installations/${installId}`, {
        method: "DELETE",
      });
      toast.success("Installation removed.");
      queryClient.invalidateQueries({ queryKey: ["installations", orgId] });
      router.push(`/dashboard/orgs/${orgId}/installations`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to remove installation.");
    } finally {
      submitting.current = false;
    }
  };

  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError) return <p className="text-sm text-red-600">Failed to load installation. Please try again.</p>;
  if (!install) return null;

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Installation Detail</h1>
          <div className="mt-1 flex items-center gap-3">
            <span className="text-[hsl(var(--muted-foreground))]">
              v{install.installed_version}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[install.status] ?? ""}`}
            >
              {install.status}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={handleFork}>
            Fork
          </Button>
          <Button variant="destructive" onClick={handleRemove}>
            Remove
          </Button>
        </div>
      </div>

      {install.update_available && install.latest_version && (
        <div className="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
          <span className="text-sm font-medium text-green-800 dark:text-green-200">
            Update available: v{install.latest_version}
          </span>
          <Button
            size="sm"
            onClick={handleViewChanges}
            disabled={loadingDiff}
          >
            {loadingDiff ? "Loading..." : "View Changes"}
          </Button>
        </div>
      )}

      {diff && (
        <div className="space-y-4">
          {diff.added.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-green-700 dark:text-green-300">
                Added ({diff.added.length})
              </h3>
              <div className="space-y-1">
                {diff.added.map((item) => (
                  <div
                    key={item.logical_id}
                    className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm dark:border-green-800 dark:bg-green-950"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-[hsl(var(--muted-foreground))]">{item.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {diff.changed.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-blue-700 dark:text-blue-300">
                Changed ({diff.changed.length})
              </h3>
              <div className="space-y-1">
                {diff.changed.map((item) => (
                  <div
                    key={item.logical_id}
                    className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-sm dark:border-blue-800 dark:bg-blue-950"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-[hsl(var(--muted-foreground))]">{item.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {diff.removed.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-red-700 dark:text-red-300">
                Removed ({diff.removed.length})
              </h3>
              <div className="space-y-1">
                {diff.removed.map((item) => (
                  <div
                    key={item.logical_id}
                    className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm dark:border-red-800 dark:bg-red-950"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-[hsl(var(--muted-foreground))]">{item.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {diff.conflicts.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-yellow-700 dark:text-yellow-300">
                Conflicts ({diff.conflicts.length})
              </h3>
              <div className="space-y-1">
                {diff.conflicts.map((item) => (
                  <div
                    key={item.logical_id}
                    className="rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm dark:border-yellow-800 dark:bg-yellow-950"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-[hsl(var(--muted-foreground))]">{item.type}</span>
                    {item.reason && (
                      <span className="ml-2 text-xs text-yellow-600 dark:text-yellow-400">
                        — {item.reason}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="rounded-lg border p-4">
        <h2 className="mb-3 text-sm font-semibold">Details</h2>
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[hsl(var(--muted-foreground))]">Pack ID</dt>
            <dd className="font-mono">{install.pack_id}</dd>
          </div>
          <div>
            <dt className="text-[hsl(var(--muted-foreground))]">Release ID</dt>
            <dd className="font-mono">{install.release_id}</dd>
          </div>
          <div>
            <dt className="text-[hsl(var(--muted-foreground))]">Installed by</dt>
            <dd>{install.installed_by}</dd>
          </div>
          <div>
            <dt className="text-[hsl(var(--muted-foreground))]">Installed at</dt>
            <dd>{new Date(install.installed_at).toLocaleString()}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
