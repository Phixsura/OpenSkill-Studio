"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface ProjectAssignment {
  id: string;
  cohort_id: string;
  project_id: string;
  deadline_override: string | null;
  late_deadline_override: string | null;
  max_submissions_override: number | null;
  participation_mode: string;
  assigned_at: string;
  project_title: string | null;
}

interface OrgProject {
  id: string;
  title: string;
  status: string;
}

export default function CohortProjectsPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const queryClient = useQueryClient();
  const [selectedProject, setSelectedProject] = useState("");
  const [deadline, setDeadline] = useState("");
  const [maxSubs, setMaxSubs] = useState("");

  const {
    data: assigned,
    isLoading: assignedLoading,
    isError: assignedError,
  } = useQuery({
    queryKey: ["cohort-projects", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectAssignment[] }>(
        `/orgs/${orgId}/cohorts/${cohortId}/projects`,
      ),
  });

  const { data: orgProjects } = useQuery({
    queryKey: ["org-projects", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgProject[] }>(`/orgs/${orgId}/projects?per_page=100`),
  });

  const assignedIds = new Set(assigned?.data.map((a) => a.project_id) || []);
  const available =
    orgProjects?.data.filter((p) => !assignedIds.has(p.id) && p.status === "published") || [];

  const assignMutation = useMutation({
    mutationFn: () => {
      const body: Record<string, unknown> = { project_id: selectedProject };
      if (deadline) body.deadline_override = deadline;
      if (maxSubs) body.max_submissions_override = parseInt(maxSubs, 10);
      return apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/projects`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-projects", cohortId] });
      setSelectedProject("");
      setDeadline("");
      setMaxSubs("");
    },
    onError: (err: Error) => alert(err.message || "Failed to assign project"),
  });

  const unassignMutation = useMutation({
    mutationFn: (projectId: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/projects/${projectId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-projects", cohortId] });
    },
    onError: (err: Error) => alert(err.message || "Failed to remove project"),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Assigned Projects</h1>

      {assignedLoading && (
        <p className="mb-4 text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}
      {assignedError && (
        <p className="mb-4 text-sm text-red-600">Failed to load projects. Please try again.</p>
      )}

      {/* Currently assigned */}
      {!assignedLoading && !assignedError && assigned?.data.length ? (
        <div className="mb-8 space-y-3">
          {assigned.data.map((a) => (
            <div key={a.id} className="rounded border p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{a.project_title || a.project_id}</span>
                <button
                  type="button"
                  onClick={() => unassignMutation.mutate(a.project_id)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Remove
                </button>
              </div>
              <div className="mt-1 flex gap-4 text-xs text-[hsl(var(--muted-foreground))]">
                <span>Mode: {a.participation_mode}</span>
                {a.deadline_override && (
                  <span>
                    Deadline: {new Date(a.deadline_override).toLocaleDateString()}
                  </span>
                )}
                {a.max_submissions_override && (
                  <span>Max submissions: {a.max_submissions_override}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="mb-8 text-sm text-[hsl(var(--muted-foreground))]">
          No projects assigned to this cohort yet.
        </p>
      )}

      {/* Assign new project */}
      {available.length > 0 && (
        <div>
          <h2 className="mb-3 text-lg font-semibold">Assign Project</h2>
          <div className="space-y-3 rounded border p-4">
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            >
              <option value="">Select a project...</option>
              {available.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
            <div className="flex gap-3">
              <input
                type="datetime-local"
                placeholder="Deadline override"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="flex-1 rounded border px-3 py-2 text-sm"
              />
              <input
                type="number"
                placeholder="Max submissions"
                value={maxSubs}
                onChange={(e) => setMaxSubs(e.target.value)}
                className="w-32 rounded border px-3 py-2 text-sm"
                min={1}
              />
            </div>
            <Button
              onClick={() => assignMutation.mutate()}
              disabled={!selectedProject || assignMutation.isPending}
            >
              Assign to Cohort
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
