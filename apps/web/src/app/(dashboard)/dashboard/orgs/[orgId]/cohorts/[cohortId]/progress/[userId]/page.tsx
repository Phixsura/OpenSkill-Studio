"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { apiWithAuth } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

interface SkillProgress {
  skill_id: string;
  name: string;
  status: string;
  exercises_done: number;
  exercises_total: number;
}

interface ProjectProgress {
  project_id: string;
  title: string;
  submission_status: string;
  score: number | null;
  submitted_at: string | null;
  is_overdue: boolean;
}

interface DrillDown {
  user_id: string;
  user_name: string | null;
  skills: SkillProgress[];
  projects: ProjectProgress[];
  last_active_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  not_started: "text-gray-500",
  in_progress: "text-blue-600",
  completed: "text-green-600",
  draft: "text-gray-500",
  submitted: "text-blue-600",
  revision_requested: "text-amber-600",
  approved: "text-green-600",
  rejected: "text-red-600",
};

export default function LearnerDrillDownPage() {
  const { orgId, cohortId, userId } = useParams<{
    orgId: string;
    cohortId: string;
    userId: string;
  }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["drill-down", cohortId, userId],
    queryFn: () =>
      apiWithAuth<{ data: DrillDown }>(
        `/orgs/${orgId}/cohorts/${cohortId}/progress/${userId}`,
      ),
  });

  const d = data?.data;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError) {
    return <p className="text-sm text-red-600">Failed to load learner progress. They may not be a member of this cohort.</p>;
  }
  if (!d) return <p>Learner not found</p>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{d.user_name || "Learner"}</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Last active: {d.last_active_at ? new Date(d.last_active_at).toLocaleString() : "Never"}
        </p>
      </div>

      {/* Skills */}
      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Skills</h2>
        {d.skills.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No skills assigned</p>
        ) : (
          <div className="space-y-2">
            {d.skills.map((s) => (
              <div key={s.skill_id} className="flex items-center justify-between rounded border px-4 py-3">
                <div>
                  <Link
                    href={`/dashboard/orgs/${orgId}/skills/${s.skill_id}`}
                    className="font-medium hover:underline"
                  >
                    {s.name}
                  </Link>
                  <span className={`ml-2 text-xs capitalize ${STATUS_COLORS[s.status] || ""}`}>
                    {s.status.replace("_", " ")}
                  </span>
                </div>
                <div className="text-sm text-[hsl(var(--muted-foreground))]">
                  {s.exercises_done}/{s.exercises_total} exercises
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Projects */}
      <section>
        <h2 className="mb-3 text-lg font-semibold">Projects</h2>
        {d.projects.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No projects assigned</p>
        ) : (
          <div className="space-y-2">
            {d.projects.map((p) => (
              <div key={p.project_id} className="flex items-center justify-between rounded border px-4 py-3">
                <div>
                  <Link
                    href={`/dashboard/orgs/${orgId}/projects/${p.project_id}`}
                    className="font-medium hover:underline"
                  >
                    {p.title}
                  </Link>
                  <span className={`ml-2 text-xs capitalize ${STATUS_COLORS[p.submission_status] || ""}`}>
                    {p.submission_status.replace("_", " ")}
                  </span>
                  {p.is_overdue && (
                    <span className="ml-2 rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700">
                      Overdue
                    </span>
                  )}
                </div>
                <div className="text-sm text-[hsl(var(--muted-foreground))]">
                  {p.score !== null ? `${p.score} pts` : "—"}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
