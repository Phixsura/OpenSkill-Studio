"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";
import { MediaPreview } from "@/components/media-preview";
import { apiWithAuth } from "@/lib/api";

interface Deliverable {
  id: string;
  name: string;
  description?: string | null;
  type: string;
  required: boolean;
  sort_order?: number;
}

interface ProjectDetail {
  id: string;
  title: string;
  description: string;
  instructions: string;
  project_type: string;
  rubric: { criterion: string; max_score: number; description?: string }[];
  difficulty: string;
  max_score: number;
  deadline: string | null;
  late_deadline: string | null;
  late_penalty_pct: number;
  deliverables: Deliverable[];
}

interface ProjectAsset {
  id: string;
  name: string;
  description: string | null;
  file_name: string;
  mime_type: string;
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

  const { data: assetsData } = useQuery({
    queryKey: ["project-assets", projectId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectAsset[] }>(`/orgs/${orgId}/projects/${projectId}/assets`),
  });

  // For workflow status: which deliverables have items in my latest submission
  const latestSubId = subsData?.data?.[0]?.id;
  const { data: latestSubDetail } = useQuery({
    queryKey: ["latest-sub-items", projectId, latestSubId],
    enabled: !!latestSubId,
    queryFn: () =>
      apiWithAuth<{ data: { items: { deliverable_id: string }[] } }>(
        `/orgs/${orgId}/projects/${projectId}/submissions/${latestSubId}`,
      ),
  });

  const project = projectData?.data;
  const submissions = subsData?.data ?? [];
  const assets = assetsData?.data ?? [];
  const completedDeliverables = new Set(
    (latestSubDetail?.data?.items ?? []).map((i) => i.deliverable_id),
  );

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

        {/* Reference Assets */}
        {assets.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold">Reference Assets</h2>
            <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {assets.map((a) => (
                <div key={a.id} className="rounded-lg border p-3">
                  <p className="text-sm font-medium">{a.name}</p>
                  {a.description && (
                    <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                      {a.description}
                    </p>
                  )}
                  <div className="mt-2">
                    <MediaPreview
                      downloadPath={`/orgs/${orgId}/projects/${projectId}/assets/${a.id}/download`}
                      mimeType={a.mime_type}
                      fileName={a.file_name}
                      className="max-h-40"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deliverables — workflow timeline for AI visual, flat list otherwise */}
        <div>
          <h2 className="text-xl font-semibold">
            {project.project_type === "ai_visual" ? "Production Workflow" : "Deliverables"}
          </h2>
          {project.project_type === "ai_visual" ? (
            <ol className="mt-3 space-y-0">
              {[...(project.deliverables ?? [])]
                .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
                .map((d, idx, arr) => {
                  const done = completedDeliverables.has(d.id);
                  return (
                    <li key={d.id} className="relative flex gap-4 pb-6 last:pb-0">
                      {/* Connector line */}
                      {idx < arr.length - 1 && (
                        <span
                          className="absolute left-[15px] top-8 h-full w-0.5 bg-[hsl(var(--border))]"
                          aria-hidden
                        />
                      )}
                      <span
                        className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                          done
                            ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200"
                            : "border bg-[hsl(var(--background))] text-[hsl(var(--muted-foreground))]"
                        }`}
                      >
                        {done ? "✓" : idx + 1}
                      </span>
                      <div className="pt-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-medium">{d.name}</span>
                          <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                            {d.type.replace("_", " ")}
                          </span>
                          {d.required && <span className="text-xs text-red-500">Required</span>}
                        </div>
                        {d.description && (
                          <p className="mt-0.5 text-sm text-[hsl(var(--muted-foreground))]">
                            {d.description}
                          </p>
                        )}
                      </div>
                    </li>
                  );
                })}
            </ol>
          ) : (
            <div className="mt-3 space-y-2">
              {(project.deliverables ?? []).map((d) => (
                <div key={d.id} className="flex items-center gap-3 rounded-lg border p-3 text-sm">
                  <span className="capitalize text-[hsl(var(--muted-foreground))]">{d.type}</span>
                  <span className="font-medium">{d.name}</span>
                  {d.required && <span className="text-xs text-red-500">Required</span>}
                </div>
              ))}
            </div>
          )}
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
