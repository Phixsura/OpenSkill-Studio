"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface OrgItem {
  id: string;
  name: string;
  role: string;
  member_count: number;
}

interface Overview {
  drafts: {
    submission_id: string;
    project_id: string;
    org_id: string;
    project_title: string;
  }[];
  peer_assessments_pending: number;
  reviews_received: {
    review_id: string;
    score: number | null;
    created_at: string;
    project_id: string;
    org_id: string;
    submission_id: string;
    project_title: string;
  }[];
  pending_reviews_to_grade: number;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data: orgsData } = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgItem[] }>("/orgs"),
  });

  const { data: overviewData } = useQuery({
    queryKey: ["my-overview"],
    queryFn: () => apiWithAuth<{ data: Overview }>("/me/overview"),
  });

  const orgs = orgsData?.data ?? [];
  const ov = overviewData?.data;
  const hasTodos =
    (ov?.drafts.length ?? 0) > 0 ||
    (ov?.peer_assessments_pending ?? 0) > 0 ||
    (ov?.pending_reviews_to_grade ?? 0) > 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome, {user?.display_name ?? "User"}
        </h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Here&apos;s an overview of your OpenSkill Studio workspace.
        </p>
      </div>

      {/* To-dos: actionable work, not infrastructure status */}
      {hasTodos && (
        <div className="space-y-3">
          <h2 className="text-xl font-semibold">To do</h2>

          {(ov?.pending_reviews_to_grade ?? 0) > 0 && (
            <div className="flex items-center justify-between rounded-lg border border-amber-300 bg-amber-50 p-4 dark:border-amber-700 dark:bg-amber-950">
              <p className="text-sm">
                <span className="font-semibold">{ov?.pending_reviews_to_grade}</span> submission
                {(ov?.pending_reviews_to_grade ?? 0) !== 1 ? "s" : ""} waiting for your review
              </p>
            </div>
          )}

          {(ov?.peer_assessments_pending ?? 0) > 0 && (
            <div className="flex items-center justify-between rounded-lg border p-4">
              <p className="text-sm">
                🤝 <span className="font-semibold">{ov?.peer_assessments_pending}</span> peer
                review{(ov?.peer_assessments_pending ?? 0) !== 1 ? "s" : ""} assigned to you
              </p>
            </div>
          )}

          {ov?.drafts.map((d) => (
            <Link
              key={d.submission_id}
              href={`/dashboard/orgs/${d.org_id}/projects/${d.project_id}/submit`}
              className="flex items-center justify-between rounded-lg border p-4 text-sm hover:shadow-sm"
            >
              <span>
                ✏️ Draft in progress — <span className="font-medium">{d.project_title}</span>
              </span>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">Continue →</span>
            </Link>
          ))}
        </div>
      )}

      {/* Recent feedback on my work */}
      {(ov?.reviews_received.length ?? 0) > 0 && (
        <div>
          <h2 className="text-xl font-semibold">Recent feedback</h2>
          <div className="mt-3 space-y-2">
            {ov?.reviews_received.map((r) => (
              <Link
                key={r.review_id}
                href={`/dashboard/orgs/${r.org_id}/projects/${r.project_id}/submissions/${r.submission_id}`}
                className="flex items-center justify-between rounded-lg border p-3 text-sm hover:shadow-sm"
              >
                <span>
                  📋 <span className="font-medium">{r.project_title}</span> was reviewed
                </span>
                <span className="flex items-center gap-3">
                  {r.score !== null && <span className="font-mono font-bold">{r.score} pts</span>}
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Organizations */}
      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Your Organizations</h2>
          <Link href="/dashboard/orgs/new">
            <Button size="sm">Create Organization</Button>
          </Link>
        </div>

        {orgs.length === 0 ? (
          <div className="mt-4 rounded-lg border border-dashed p-8 text-center">
            <p className="text-[hsl(var(--muted-foreground))]">
              You haven&apos;t joined any organizations yet.
            </p>
            <Link href="/dashboard/orgs/new">
              <Button className="mt-3">Create your first organization</Button>
            </Link>
          </div>
        ) : (
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {orgs.map((org) => (
              <Link
                key={org.id}
                href={`/dashboard/orgs/${org.id}`}
                className="block rounded-lg border p-4 transition-shadow hover:shadow-md"
              >
                <h3 className="font-semibold">{org.name}</h3>
                <div className="mt-2 flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 capitalize">
                    {org.role}
                  </span>
                  <span>{org.member_count} member{org.member_count !== 1 ? "s" : ""}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick links */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/dashboard/portfolio"
          className="rounded-lg border p-5 transition-shadow hover:shadow-sm"
        >
          <h3 className="font-semibold">Portfolio</h3>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Manage your public profile and showcase your work.
          </p>
        </Link>
        <Link
          href="/dashboard/settings"
          className="rounded-lg border p-5 transition-shadow hover:shadow-sm"
        >
          <h3 className="font-semibold">Settings</h3>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Update your display name and account preferences.
          </p>
        </Link>
      </div>
    </div>
  );
}
