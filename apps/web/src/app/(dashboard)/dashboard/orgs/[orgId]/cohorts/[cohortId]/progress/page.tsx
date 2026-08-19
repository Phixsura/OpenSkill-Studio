"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { apiWithAuth } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

interface CohortMember {
  id: string;
  user_id: string;
  role: string;
  user_name: string | null;
  joined_at: string;
}

interface CohortProgress {
  total_learners: number;
  total_skills_assigned: number;
  avg_skill_completion_pct: number;
  overdue_submissions: number;
  inactive_learners_7d: number;
  projects: Array<{
    project_id: string;
    title: string;
    submitted: number;
    approved: number;
    not_started: number;
    overdue: number;
  }>;
}

export default function CohortProgressPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();

  const { data: progressData } = useQuery({
    queryKey: ["cohort-progress-stats", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortProgress }>(
        `/orgs/${orgId}/cohorts/${cohortId}/progress`,
      ),
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["cohort-members-progress", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortMember[]; meta: { total: number } }>(
        `/orgs/${orgId}/cohorts/${cohortId}/members?role=learner&per_page=100`,
      ),
  });

  const stats = progressData?.data;
  const learners = data?.data ?? [];

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Learner Progress</h1>

      {/* Aggregate stats */}
      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xl font-bold">{stats.total_learners}</div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">Learners</div>
          </div>
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xl font-bold">{stats.avg_skill_completion_pct}%</div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">Skill Completion</div>
          </div>
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xl font-bold text-red-600">{stats.overdue_submissions}</div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">Overdue</div>
          </div>
          <div className="rounded-lg border p-3 text-center">
            <div className="text-xl font-bold text-amber-600">{stats.inactive_learners_7d}</div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">Inactive (7d)</div>
          </div>
        </div>
      )}

      <p className="mb-4 text-sm text-[hsl(var(--muted-foreground))]">
        Click a learner to see their detailed skill and project progress.
      </p>

      {isError && <p className="mb-4 text-sm text-red-600">Failed to load learner list.</p>}

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      ) : learners.length === 0 ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">No learners enrolled yet.</p>
      ) : (
        <div className="space-y-2">
          {learners.map((m) => (
            <Link
              key={m.user_id}
              href={`/dashboard/orgs/${orgId}/cohorts/${cohortId}/progress/${m.user_id}`}
              className="flex items-center justify-between rounded border px-4 py-3 hover:bg-[hsl(var(--secondary)/0.5)]"
            >
              <div>
                <span className="font-medium">{m.user_name || m.user_id}</span>
              </div>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                Joined {new Date(m.joined_at).toLocaleDateString()}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
