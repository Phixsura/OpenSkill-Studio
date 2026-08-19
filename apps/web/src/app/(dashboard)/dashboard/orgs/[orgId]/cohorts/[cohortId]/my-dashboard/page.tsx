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

interface RevisionItem {
  submission_id: string;
  project_id: string;
  updated_at: string;
}

interface PeerReviewItem {
  assessment_id: string;
  submission_id: string;
  assigned_at: string;
}

interface FeedbackItem {
  review_id: string;
  submission_id: string;
  score: number | null;
  feedback: string;
  created_at: string;
  reviewer_type: string;
}

interface LearnerDashboard {
  cohort: {
    id: string;
    name: string;
    description: string | null;
    status: string;
    member_count: number;
  };
  assigned_skills: SkillProgress[];
  assigned_projects: ProjectProgress[];
  needs_revision: RevisionItem[];
  pending_peer_reviews: PeerReviewItem[];
  recent_feedback: FeedbackItem[];
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

interface CohortSummary {
  id: string;
  name: string;
  status: string;
}

export default function MyDashboardPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["my-cohort-dashboard", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: LearnerDashboard }>(
        `/orgs/${orgId}/cohorts/${cohortId}/my-dashboard`,
      ),
  });

  // Fetch all cohorts the learner belongs to (for switching)
  const { data: myCohorts } = useQuery({
    queryKey: ["my-cohorts", orgId],
    queryFn: () =>
      apiWithAuth<{ data: CohortSummary[] }>(`/orgs/${orgId}/my-cohorts`),
  });

  const d = data?.data;
  const otherCohorts = myCohorts?.data.filter((c) => c.id !== cohortId) ?? [];

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError) {
    return <p className="text-sm text-red-600">Failed to load dashboard. You may not be a member of this cohort.</p>;
  }
  if (!d) return null;

  return (
    <div>
      <div className="mb-1 flex items-center gap-3">
        <h1 className="text-2xl font-bold">{d.cohort.name}</h1>
        {otherCohorts.length > 0 && (
          <select
            className="rounded border px-2 py-1 text-sm"
            value=""
            onChange={(e) => {
              if (e.target.value) {
                window.location.href = `/dashboard/orgs/${orgId}/cohorts/${e.target.value}/my-dashboard`;
              }
            }}
          >
            <option value="">Switch cohort...</option>
            {otherCohorts.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        )}
      </div>
      {d.cohort.description && (
        <p className="mb-6 text-sm text-[hsl(var(--muted-foreground))]">
          {d.cohort.description}
        </p>
      )}

      {/* Skills */}
      {d.assigned_skills.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">Assigned Skills</h2>
          <div className="space-y-2">
            {d.assigned_skills.map((s) => (
              <Link
                key={s.skill_id}
                href={`/dashboard/orgs/${orgId}/skills/${s.skill_id}`}
                className="flex items-center justify-between rounded border px-4 py-3 hover:bg-[hsl(var(--secondary)/0.5)]"
              >
                <div>
                  <span className="font-medium">{s.name}</span>
                  <span className={`ml-2 text-xs capitalize ${STATUS_COLORS[s.status] || ""}`}>
                    {s.status.replace("_", " ")}
                  </span>
                </div>
                <div className="text-sm text-[hsl(var(--muted-foreground))]">
                  {s.exercises_done}/{s.exercises_total} exercises
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Projects */}
      {d.assigned_projects.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">Assigned Projects</h2>
          <div className="space-y-2">
            {d.assigned_projects.map((p) => (
              <Link
                key={p.project_id}
                href={`/dashboard/orgs/${orgId}/projects/${p.project_id}`}
                className="flex items-center justify-between rounded border px-4 py-3 hover:bg-[hsl(var(--secondary)/0.5)]"
              >
                <div>
                  <span className="font-medium">{p.title}</span>
                  <span
                    className={`ml-2 text-xs capitalize ${STATUS_COLORS[p.submission_status] || ""}`}
                  >
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
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Work Needing Revision */}
      {d.needs_revision.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold text-amber-600">⚠ Work Needing Revision</h2>
          <div className="space-y-2">
            {d.needs_revision.map((r) => (
              <Link
                key={r.submission_id}
                href={`/dashboard/orgs/${orgId}/projects/${r.project_id}`}
                className="flex items-center justify-between rounded border border-amber-200 bg-amber-50 px-4 py-3 hover:bg-amber-100 dark:border-amber-800 dark:bg-amber-950 dark:hover:bg-amber-900"
              >
                <span className="text-sm font-medium">Revision requested</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(r.updated_at).toLocaleDateString()}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Pending Peer Reviews */}
      {d.pending_peer_reviews.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">📝 Pending Peer Reviews</h2>
          <div className="space-y-2">
            {d.pending_peer_reviews.map((pr) => (
              <div
                key={pr.assessment_id}
                className="flex items-center justify-between rounded border px-4 py-3"
              >
                <span className="text-sm">Peer review assigned</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(pr.assigned_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Recent Feedback */}
      {d.recent_feedback.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">💬 Recent Feedback</h2>
          <div className="space-y-2">
            {d.recent_feedback.map((fb) => (
              <div key={fb.review_id} className="rounded border px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 capitalize">
                    {fb.reviewer_type === "ai" ? "🤖 AI Review" : "👤 Instructor"}
                  </span>
                  {fb.score !== null && (
                    <span className="text-sm font-medium">{fb.score} pts</span>
                  )}
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {new Date(fb.created_at).toLocaleDateString()}
                  </span>
                </div>
                {fb.feedback && (
                  <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                    {fb.feedback}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {d.assigned_skills.length === 0 && d.assigned_projects.length === 0 && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No skills or projects assigned to this cohort yet.
        </p>
      )}

      {/* Commercial opportunities link */}
      <section className="mt-8 rounded-lg border border-dashed p-4">
        <h2 className="mb-1 text-lg font-semibold">🚀 Commercial Opportunities</h2>
        <p className="mb-3 text-sm text-[hsl(var(--muted-foreground))]">
          Browse open commercial projects you can apply to work on.
        </p>
        <Link
          href={`/dashboard/orgs/${orgId}/opportunities`}
          className="inline-block rounded bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90"
        >
          Browse Opportunities →
        </Link>
      </section>
    </div>
  );
}
