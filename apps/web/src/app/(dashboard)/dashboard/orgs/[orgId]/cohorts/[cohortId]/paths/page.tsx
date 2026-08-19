"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface AssignedPath {
  path_id: string;
  path_name: string;
  assigned_at: string;
}

interface OrgPath {
  id: string;
  name: string;
  status: string;
}

export default function CohortPathsPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const queryClient = useQueryClient();
  const [selectedPathId, setSelectedPathId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["cohort-paths", orgId, cohortId],
    queryFn: () =>
      apiWithAuth<{ data: AssignedPath[] }>(
        `/orgs/${orgId}/cohorts/${cohortId}/paths`,
      ),
  });

  const { data: orgPathsData } = useQuery({
    queryKey: ["org-paths-published", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgPath[]; meta: { total: number } }>(
        `/orgs/${orgId}/paths?status=published`,
      ),
  });

  const assignMutation = useMutation({
    mutationFn: (pathId: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/paths`, {
        method: "POST",
        body: JSON.stringify({ path_id: pathId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-paths", orgId, cohortId] });
      setSelectedPathId("");
      toast.success("Path assigned to cohort");
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Failed to assign path");
    },
  });

  const unassignMutation = useMutation({
    mutationFn: (pathId: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/paths/${pathId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-paths", orgId, cohortId] });
      toast.success("Path unassigned");
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Failed to unassign path");
    },
  });

  const paths = data?.data ?? [];
  const orgPaths = (orgPathsData?.data ?? []).filter(
    (p) => p.status === "published",
  );
  const assignedIds = new Set(paths.map((p) => p.path_id));
  const availablePaths = orgPaths.filter((p) => !assignedIds.has(p.id));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Learning Paths</h2>
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Assign published learning paths to this cohort.
        </p>
      </div>

      {/* Assign form */}
      {availablePaths.length > 0 && (
        <div className="flex items-end gap-3">
          <div className="flex-1">
            <label className="block text-sm font-medium">Assign a path</label>
            <select
              value={selectedPathId}
              onChange={(e) => setSelectedPathId(e.target.value)}
              className="mt-1 w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="">Select a learning path...</option>
              {availablePaths.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <Button
            size="sm"
            disabled={!selectedPathId || assignMutation.isPending}
            onClick={() => selectedPathId && assignMutation.mutate(selectedPathId)}
          >
            Assign
          </Button>
        </div>
      )}

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && paths.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No learning paths assigned to this cohort yet.
        </div>
      )}

      {paths.length > 0 && (
        <div className="space-y-3">
          {paths.map((p) => (
            <div
              key={p.path_id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div>
                <span className="font-medium">{p.path_name}</span>
                <span className="ml-3 text-xs text-[hsl(var(--muted-foreground))]">
                  Assigned {new Date(p.assigned_at).toLocaleDateString()}
                </span>
              </div>
              <Button
                size="sm"
                variant="ghost"
                className="text-red-600 hover:text-red-700"
                disabled={unassignMutation.isPending}
                onClick={() => {
                  if (window.confirm("Unassign this path from the cohort?")) {
                    unassignMutation.mutate(p.path_id);
                  }
                }}
              >
                Remove
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
