"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
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

export default function ProjectsListPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["projects", orgId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectItem[]; meta: { total: number } }>(
        `/orgs/${orgId}/projects`,
      ),
  });

  const projects = data?.data ?? [];

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
    </div>
  );
}
