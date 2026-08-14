"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Deliverable {
  id: string;
  name: string;
  type: string;
  required: boolean;
}

interface ProjectDetail {
  id: string;
  title: string;
  description: string;
  instructions: string;
  rubric: { criterion: string; max_score: number; description?: string }[];
  difficulty: string;
  max_score: number;
  deadline: string | null;
  late_deadline: string | null;
  late_penalty_pct: number;
  deliverables: Deliverable[];
}

interface SubmissionItem {
  id: string;
  version: number;
  status: string;
  submitted_at: string | null;
  final_score: number | null;
}

export default function ProjectDetailPage() {
  const { orgId, projectId } = useParams<{ orgId: string; projectId: string }>();

  const { data: projectData, isLoading, isError } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => apiWithAuth<{ data: ProjectDetail }>(`/orgs/${orgId}/projects/${projectId}`),
  });

  const { data: subsData } = useQuery({
    queryKey: ["submissions", projectId],
    queryFn: () =>
      apiWithAuth<{ data: SubmissionItem[] }>(`/orgs/${orgId}/projects/${projectId}/submissions`),
  });

  const project = projectData?.data;
  const submissions = subsData?.data ?? [];

  if (isLoading) return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError || !project) return <p className="text-[hsl(var(--destructive))]">Failed to load project.</p>;

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold">{project.title}</h1>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">{project.description}</p>
        </div>

        <div className="prose prose-sm max-w-none dark:prose-invert">
          <h2>Instructions</h2>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{project.instructions}</ReactMarkdown>
        </div>

        {/* Deliverables */}
        <div>
          <h2 className="text-xl font-semibold">Deliverables</h2>
          <div className="mt-3 space-y-2">
            {(project.deliverables ?? []).map((d) => (
              <div key={d.id} className="flex items-center gap-3 rounded-lg border p-3 text-sm">
                <span className="capitalize text-[hsl(var(--muted-foreground))]">{d.type}</span>
                <span className="font-medium">{d.name}</span>
                {d.required && <span className="text-xs text-red-500">Required</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Rubric */}
        <div>
          <h2 className="text-xl font-semibold">Rubric</h2>
          <div className="mt-3 overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-[hsl(var(--secondary))]">
                <tr>
                  <th className="px-4 py-2 text-left">Criterion</th>
                  <th className="px-4 py-2 text-right">Max Score</th>
                </tr>
              </thead>
              <tbody>
                {(project.rubric ?? []).map((r, i) => (
                  <tr key={i} className="border-t">
                    <td className="px-4 py-2">{r.criterion}</td>
                    <td className="px-4 py-2 text-right">{r.max_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Submissions */}
        <div>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">My Submissions</h2>
            <Link href={`/dashboard/orgs/${orgId}/projects/${projectId}/submit`}>
              <Button>New Submission</Button>
            </Link>
          </div>
          <div className="mt-3 space-y-2">
            {submissions.length === 0 && (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">No submissions yet.</p>
            )}
            {submissions.map((s) => (
              <Link
                key={s.id}
                href={`/dashboard/orgs/${orgId}/projects/${projectId}/submissions/${s.id}`}
                className="flex items-center justify-between rounded-lg border p-3 text-sm hover:shadow-sm"
              >
                <span>v{s.version} — <span className="capitalize">{s.status.replace("_", " ")}</span></span>
                {s.final_score !== null && (
                  <span className="font-mono font-bold">{s.final_score}/{project.max_score}</span>
                )}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <aside className="space-y-4">
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-semibold">Details</h3>
          <dl className="mt-3 space-y-2 text-sm">
            <div>
              <dt className="text-[hsl(var(--muted-foreground))]">Difficulty</dt>
              <dd className="capitalize">{project.difficulty}</dd>
            </div>
            <div>
              <dt className="text-[hsl(var(--muted-foreground))]">Max Score</dt>
              <dd>{project.max_score}</dd>
            </div>
            {project.deadline && (
              <div>
                <dt className="text-[hsl(var(--muted-foreground))]">Deadline</dt>
                <dd>{new Date(project.deadline).toLocaleDateString()}</dd>
              </div>
            )}
            {project.late_penalty_pct > 0 && (
              <div>
                <dt className="text-[hsl(var(--muted-foreground))]">Late Penalty</dt>
                <dd>{project.late_penalty_pct}%</dd>
              </div>
            )}
          </dl>
        </div>
      </aside>
    </div>
  );
}
