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

export default function CohortProgressPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["cohort-members-progress", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortMember[]; meta: { total: number } }>(
        `/orgs/${orgId}/cohorts/${cohortId}/members?role=learner&per_page=100`,
      ),
  });

  const learners = data?.data ?? [];

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Learner Progress</h1>
      <p className="mb-6 text-sm text-[hsl(var(--muted-foreground))]">
        Click a learner to see their detailed skill and project progress.
      </p>

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
