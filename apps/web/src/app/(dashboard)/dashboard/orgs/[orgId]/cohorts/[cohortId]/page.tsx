"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { apiWithAuth } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

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
}

export default function CohortDetailPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();

  const { data: cohort, isError: cohortError } = useQuery({
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

  const c = cohort?.data;
  const p = progress?.data;

  if (cohortError) {
    return <p className="text-sm text-red-600">Failed to load cohort. It may not exist or you don&apos;t have access.</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{c?.name || "Cohort"}</h1>
        {c?.description && (
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {c.description}
          </p>
        )}
      </div>

      {/* Quick stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold">{p?.total_learners ?? "—"}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Learners</div>
        </div>
        <div className="rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold">{p?.total_skills_assigned ?? "—"}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Skills Assigned</div>
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
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading progress...</p>
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
