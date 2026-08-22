"use client";

import Link from "next/link";
import { toast } from "sonner";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface ProjectProgress {
  project_id: string;
  title: string;
  submitted: number;
  approved: number;
  revision_requested: number;
  not_started: number;
  overdue: number;
  total_assignees: number;
  deadline: string | null;
}

interface CohortProgress {
  total_learners: number;
  total_skills_assigned: number;
  projects: ProjectProgress[];
  overdue_submissions: number;
}

interface CohortDetail {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  status: string;
  member_count: number;
  starts_at: string | null;
  ends_at: string | null;
  max_learners: number | null;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  archived: "bg-gray-100 text-gray-800",
};

const NEXT_STATUS: Record<string, { label: string; target: string }> = {
  draft: { label: "Activate Cohort", target: "active" },
  active: { label: "Complete Cohort", target: "completed" },
  completed: { label: "Archive Cohort", target: "archived" },
};

export default function CohortDetailPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editStartsAt, setEditStartsAt] = useState("");
  const [editEndsAt, setEditEndsAt] = useState("");
  const [editMaxLearners, setEditMaxLearners] = useState("");

  const { data: cohort, isLoading: cohortLoading, isError: cohortError } = useQuery({
    queryKey: ["cohort", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortDetail }>(`/orgs/${orgId}/cohorts/${cohortId}`),
  });

  const { data: progress, isLoading, isError: progressError } = useQuery({
    queryKey: ["cohort-progress", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortProgress }>(
        `/orgs/${orgId}/cohorts/${cohortId}/progress`,
      ),
  });

  const statusMutation = useMutation({
    mutationFn: (newStatus: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort", cohortId] });
      queryClient.invalidateQueries({ queryKey: ["cohort-progress", cohortId] });
      queryClient.invalidateQueries({ queryKey: ["cohorts", orgId] });
    },
    onError: (err: Error) => toast.error(err.message || "Failed to update status"),
  });

  const editMutation = useMutation({
    mutationFn: (fields: Record<string, unknown>) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}`, {
        method: "PUT",
        body: JSON.stringify(fields),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort", cohortId] });
      queryClient.invalidateQueries({ queryKey: ["cohorts", orgId] });
      setShowEdit(false);
    },
    onError: (err: Error) => toast.error(err.message || "Failed to update cohort"),
  });

  const deleteMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohorts", orgId] });
      router.push(`/dashboard/orgs/${orgId}/cohorts`);
    },
    onError: (err: Error) => toast.error(err.message || "Failed to delete cohort"),
  });

  const c = cohort?.data;
  const p = progress?.data;

  if (cohortLoading) {
    return (
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Loading cohort...
      </p>
    );
  }

  if (cohortError) {
    return (
      <p className="text-sm text-red-600">
        Failed to load cohort. It may not exist or you don&apos;t have access.
      </p>
    );
  }

  const nextAction = c ? NEXT_STATUS[c.status] : null;

  const startEditing = () => {
    if (!c) return;
    setEditName(c.name);
    setEditDescription(c.description || "");
    setEditStartsAt(c.starts_at ? c.starts_at.slice(0, 16) : "");
    setEditEndsAt(c.ends_at ? c.ends_at.slice(0, 16) : "");
    setEditMaxLearners(c.max_learners?.toString() || "");
    setShowEdit(true);
  };

  const handleStatusChange = (target: string) => {
    if (target !== "active") {
      if (!confirm("Are you sure? This action cannot be undone.")) return;
    }
    statusMutation.mutate(target);
  };

  return (
    <div>
      {/* Header with status + actions */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{c?.name || "Cohort"}</h1>
            {c && (
              <span
                className={`rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_COLORS[c.status] || ""}`}
              >
                {c.status}
              </span>
            )}
          </div>
          {c?.description && (
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              {c.description}
            </p>
          )}
          {c && (c.starts_at || c.ends_at) && (
            <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
              {c.starts_at && `Starts ${new Date(c.starts_at).toLocaleDateString()}`}
              {c.starts_at && c.ends_at && " · "}
              {c.ends_at && `Ends ${new Date(c.ends_at).toLocaleDateString()}`}
              {c.max_learners && ` · Max ${c.max_learners} learners`}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {nextAction && (
            <Button
              size="sm"
              onClick={() => handleStatusChange(nextAction.target)}
              disabled={statusMutation.isPending}
            >
              {statusMutation.isPending ? "Updating..." : nextAction.label}
            </Button>
          )}
          {c && (
            <Button variant="outline" size="sm" onClick={startEditing}>
              Edit
            </Button>
          )}
          {c?.status === "draft" && (
            <Button
              variant="outline"
              size="sm"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm("Delete this cohort? This cannot be undone.")) {
                  deleteMutation.mutate();
                }
              }}
            >
              Delete
            </Button>
          )}
        </div>
      </div>

      {/* Edit form */}
      {showEdit && (
        <div className="mb-6 space-y-3 rounded-lg border p-4">
          <h2 className="text-lg font-semibold">Edit Cohort</h2>
          <input
            type="text"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            placeholder="Cohort name"
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            placeholder="Description"
            rows={2}
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                Start date
              </label>
              <input
                type="datetime-local"
                value={editStartsAt}
                onChange={(e) => setEditStartsAt(e.target.value)}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                End date
              </label>
              <input
                type="datetime-local"
                value={editEndsAt}
                onChange={(e) => setEditEndsAt(e.target.value)}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>
            <div className="w-32">
              <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                Max learners
              </label>
              <input
                type="number"
                value={editMaxLearners}
                onChange={(e) => setEditMaxLearners(e.target.value)}
                min={1}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() =>
                editMutation.mutate({
                  name: editName,
                  description: editDescription || undefined,
                  starts_at: editStartsAt || undefined,
                  ends_at: editEndsAt || undefined,
                  max_learners: editMaxLearners
                    ? parseInt(editMaxLearners, 10)
                    : undefined,
                })
              }
              disabled={editMutation.isPending}
            >
              {editMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
            <Button variant="outline" onClick={() => setShowEdit(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Quick stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold">{p?.total_learners ?? "—"}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Learners</div>
        </div>
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold">{p?.total_skills_assigned ?? "—"}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">
            Skills Assigned
          </div>
        </div>
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold">{p?.projects.length ?? "—"}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Projects</div>
        </div>
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold text-red-600">
            {p?.overdue_submissions ?? "—"}
          </div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Overdue</div>
        </div>
      </div>

      {/* Navigation links */}
      <div className="mb-8 flex gap-3">
        <Link
          href={`/dashboard/orgs/${orgId}/cohorts/${cohortId}/members`}
          className="rounded border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Manage Members
        </Link>
        <Link
          href={`/dashboard/orgs/${orgId}/cohorts/${cohortId}/skills`}
          className="rounded border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Assign Skills
        </Link>
        <Link
          href={`/dashboard/orgs/${orgId}/cohorts/${cohortId}/projects`}
          className="rounded border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Assign Projects
        </Link>
      </div>

      {/* Project progress table */}
      {progressError ? (
        <p className="text-sm text-red-600">Failed to load progress data.</p>
      ) : isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Loading progress...
        </p>
      ) : p?.projects.length ? (
        <div>
          <h2 className="mb-3 text-lg font-semibold">Project Progress</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-[hsl(var(--muted-foreground))]">
                  <th className="px-3 py-2">Project</th>
                  <th className="px-3 py-2">Not Started</th>
                  <th className="px-3 py-2">Submitted</th>
                  <th className="px-3 py-2">Revision</th>
                  <th className="px-3 py-2">Approved</th>
                  <th className="px-3 py-2">Overdue</th>
                  <th className="px-3 py-2">Deadline</th>
                </tr>
              </thead>
              <tbody>
                {p.projects.map((proj) => (
                  <tr key={proj.project_id} className="border-b">
                    <td className="px-3 py-2 font-medium">{proj.title}</td>
                    <td className="px-3 py-2">{proj.not_started}</td>
                    <td className="px-3 py-2">{proj.submitted}</td>
                    <td className="px-3 py-2">{proj.revision_requested}</td>
                    <td className="px-3 py-2 text-green-600">{proj.approved}</td>
                    <td className="px-3 py-2 text-red-600">{proj.overdue || "—"}</td>
                    <td className="px-3 py-2 text-xs">
                      {proj.deadline
                        ? new Date(proj.deadline).toLocaleDateString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No projects assigned to this cohort yet.
        </p>
      )}
    </div>
  );
}
