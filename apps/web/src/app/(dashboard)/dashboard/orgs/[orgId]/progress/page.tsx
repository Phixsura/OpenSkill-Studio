"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface ProgressData {
  skills_total: number;
  skills_completed: number;
  skills_in_progress: number;
  exercises_total: number;
  exercises_completed: number;
  completion_percentage: number;
  categories: { id: string; name: string; skills_total: number; skills_completed: number; completion_percentage: number }[];
}

export default function ProgressPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["progress", orgId],
    queryFn: () => apiWithAuth<ProgressData>(`/orgs/${orgId}/progress/me`),
  });

  if (isLoading || !data) {
    return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Progress</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Track your learning progress across all skills.
        </p>
      </div>

      {/* Overall stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Completion" value={`${data.completion_percentage}%`} />
        <StatCard label="Skills Completed" value={`${data.skills_completed}/${data.skills_total}`} />
        <StatCard label="In Progress" value={String(data.skills_in_progress)} />
        <StatCard label="Exercises Done" value={`${data.exercises_completed}/${data.exercises_total}`} />
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex items-center justify-between text-sm">
          <span>Overall Progress</span>
          <span className="font-mono">{data.completion_percentage}%</span>
        </div>
        <div className="mt-2 h-3 rounded-full bg-[hsl(var(--secondary))]">
          <div
            className="h-full rounded-full bg-green-500 transition-all"
            style={{ width: `${data.completion_percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}
