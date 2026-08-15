"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface PendingSub {
  id: string;
  project_id: string;
  user_id: string;
  version: number;
  status: string;
  submitted_at: string;
  is_late: boolean;
  author_name: string;
  project_title: string;
}

export default function ReviewDashboardPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["pending-reviews", orgId],
    queryFn: () =>
      apiWithAuth<{ data: PendingSub[]; meta: { total: number } }>(
        `/orgs/${orgId}/reviews/pending`,
      ),
  });

  const submissions = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Pending Reviews</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          {total} submission{total !== 1 ? "s" : ""} awaiting review.
        </p>
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && submissions.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No pending reviews. 🎉
        </div>
      )}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-[hsl(var(--secondary))]">
            <tr>
              <th className="px-4 py-3 text-left">Learner</th>
              <th className="px-4 py-3 text-left">Project</th>
              <th className="px-4 py-3 text-left">Version</th>
              <th className="px-4 py-3 text-left">Submitted</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-right" />
            </tr>
          </thead>
          <tbody>
            {submissions.map((s) => (
              <tr key={s.id} className="border-t hover:bg-[hsl(var(--secondary))]">
                <td className="px-4 py-3">
                  <span className="flex items-center gap-2 font-medium">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-xs font-semibold uppercase">
                      {s.author_name?.[0] ?? "?"}
                    </span>
                    {s.author_name}
                  </span>
                </td>
                <td className="px-4 py-3">{s.project_title}</td>
                <td className="px-4 py-3">v{s.version}</td>
                <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                  {s.submitted_at ? new Date(s.submitted_at).toLocaleString() : "—"}
                </td>
                <td className="px-4 py-3">
                  {s.is_late && <span className="text-yellow-600">Late</span>}
                  {!s.is_late && <span className="text-green-600">On time</span>}
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/dashboard/orgs/${orgId}/reviews/${s.id}`}
                    className="rounded-md bg-[hsl(var(--primary))] px-3 py-1.5 text-xs font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
                  >
                    Review →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {submissions.length < total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {submissions.length} of {total} pending reviews
        </p>
      )}
    </div>
  );
}
