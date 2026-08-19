"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface ProjectItem {
  id: string;
  title: string;
  slug: string;
  description: string;
  difficulty: string;
  max_score: number;
  deadline: string | null;
  status: string;
}

interface CohortItem {
  id: string;
  name: string;
}

export default function ProjectsListPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [cohortFilter, setCohortFilter] = useState<string>("");

  const { data: cohortsData } = useQuery({
    queryKey: ["my-cohorts", orgId],
    queryFn: () =>
      apiWithAuth<{ data: CohortItem[] }>(`/orgs/${orgId}/my-cohorts`),
  });

  const cohortParam = cohortFilter ? `?cohort_id=${cohortFilter}` : "";

  const { data, isLoading, isError } = useQuery({
    queryKey: ["projects", orgId, cohortFilter],
    queryFn: () =>
      apiWithAuth<{ data: ProjectItem[]; meta: { total: number } }>(
        `/orgs/${orgId}/projects${cohortParam}`,
      ),
  });

  const projects = data?.data ?? [];
  const cohorts = cohortsData?.data ?? [];

  const formatDeadline = (d: string | null) => {
    if (!d) return "No deadline";
    const date = new Date(d);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    if (days < 0) return "Past due";
    if (days === 0) return "Due today";
    if (days === 1) return "Due tomorrow";
    return `${days} days left`;
  };

  return (
    <div className="space-y-6">
      {isError && <p className="mb-4 text-sm text-red-600">Failed to load projects. Please try again.</p>}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            View and submit project assignments.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/projects/new`}>
          <Button size="sm">New Project</Button>
        </Link>
      </div>

      {/* Cohort filter */}
      {cohorts.length > 0 && (
        <div className="flex items-center gap-2">
          <label className="text-sm text-[hsl(var(--muted-foreground))]">Filter by cohort:</label>
          <select
            value={cohortFilter}
            onChange={(e) => setCohortFilter(e.target.value)}
            className="rounded border px-2 py-1 text-sm"
          >
            <option value="">All projects</option>
            {cohorts.map((co) => (
              <option key={co.id} value={co.id}>
                {co.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && projects.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No projects yet.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((p) => (
          <Link
            key={p.id}
            href={`/dashboard/orgs/${orgId}/projects/${p.id}`}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">{p.title}</h3>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {p.description}
            </p>
            <div className="mt-3 flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
              <span className="capitalize">{p.difficulty}</span>
              <span>·</span>
              <span>{p.max_score} pts</span>
              <span>·</span>
              <span className={p.deadline && new Date(p.deadline) < new Date() ? "text-red-600" : ""}>
                {formatDeadline(p.deadline)}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {data?.meta && projects.length < data.meta.total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {projects.length} of {data.meta.total} projects
        </p>
      )}
    </div>
  );
}
