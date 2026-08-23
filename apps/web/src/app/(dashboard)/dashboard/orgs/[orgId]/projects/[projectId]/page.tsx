"use client";

import Link from "next/link";
import { toast } from "sonner";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";
import { MediaPreview } from "@/components/media-preview";
import { PeerReviewSection } from "@/components/peer-review-section";
import { apiWithAuth } from "@/lib/api";

interface CreatorAssignment {
  user_id: string;
  user_name: string | null;
  assigned_at: string;
}

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
  user_id: string;
  version: number;
  status: string;
  submitted_at: string | null;
  final_score: number | null;
  author_name: string;
}

export default function ProjectDetailPage() {
  const { orgId, projectId } = useParams<{ orgId: string; projectId: string }>();
  const queryClient = useQueryClient();
  const [creatorUserId, setCreatorUserId] = useState("");

  const { data: projectData, isLoading, isError } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => apiWithAuth<{ data: ProjectDetail }>(`/orgs/${orgId}/projects/${projectId}`),
  });

  const { data: subsData } = useQuery({
    queryKey: ["submissions", projectId],
    queryFn: () =>
      apiWithAuth<{ data: SubmissionItem[] }>(`/orgs/${orgId}/projects/${projectId}/submissions`),
  });

  const { data: orgData } = useQuery({
    queryKey: ["org", orgId],
    queryFn: () => apiWithAuth<{ data: { role: string | null } }>(`/orgs/${orgId}`),
  });
  const orgRole = orgData?.data?.role;
  const isInstructor = ["owner", "admin", "instructor"].includes(orgRole ?? "");

  const { data: meData } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiWithAuth<{ data: { id: string } }>(`/auth/me`),
  });
  const myId = meData?.data?.id;

  const { data: assetsData } = useQuery({
    queryKey: ["project-assets", projectId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectAsset[] }>(`/orgs/${orgId}/projects/${projectId}/assets`),
  });

  // For workflow status: pull the full items of MY latest submission so each
  // stage can show completion state + the latest submitted asset. Instructors
  // see everyone's rows in subsData, so filter to own first.
  const mySubs = (subsData?.data ?? []).filter((s) => myId != null && s.user_id === myId);
  const latestSubId = mySubs[0]?.id;
  const { data: latestSubDetail } = useQuery({
    queryKey: ["latest-sub-items", projectId, latestSubId],
    enabled: !!latestSubId,
    queryFn: () =>
      apiWithAuth<{
        data: {
          items: {
            id: string;
            deliverable_id: string;
            type: string;
            file_name: string | null;
            mime_type: string | null;
            version: number;
          }[];
        };
      }>(`/orgs/${orgId}/projects/${projectId}/submissions/${latestSubId}`),
  });

  const { data: creatorsData } = useQuery({
    queryKey: ["project-creators", projectId],
    enabled: isInstructor,
    queryFn: () =>
      apiWithAuth<{ data: CreatorAssignment[] }>(
        `/orgs/${orgId}/projects/${projectId}/creators`,
      ),
  });

  const assignCreatorMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/projects/${projectId}/creators`, {
        method: "POST",
        body: JSON.stringify({ user_id: creatorUserId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-creators", projectId] });
      setCreatorUserId("");
    },
    onError: (err: Error) => toast.error(err.message || "Failed to assign creator"),
  });

  const removeCreatorMutation = useMutation({
    mutationFn: (userId: string) =>
      apiWithAuth(`/orgs/${orgId}/projects/${projectId}/creators/${userId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-creators", projectId] });
    },
    onError: (err: Error) => toast.error(err.message || "Failed to remove creator"),
  });

  const project = projectData?.data;
  const submissions = subsData?.data ?? [];
  const assets = assetsData?.data ?? [];
  const creators = creatorsData?.data ?? [];

  // Latest item per deliverable (highest version) from my latest submission.
  const latestItemByDeliverable = new Map<
    string,
    { id: string; type: string; file_name: string | null; mime_type: string | null; version: number }
  >();
  for (const it of latestSubDetail?.data?.items ?? []) {
    const prev = latestItemByDeliverable.get(it.deliverable_id);
    if (!prev || it.version > prev.version) latestItemByDeliverable.set(it.deliverable_id, it);
  }
  const completedDeliverables = new Set(latestItemByDeliverable.keys());

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
            (() => {
              const ordered = [...(project.deliverables ?? [])].sort(
                (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0),
              );
              // "Current" = the work frontier: the first incomplete stage at or
              // after the last completed one. This way, optional stages the
              // learner skipped to reach a later stage read as "Not Started"
              // rather than falsely grabbing the "In Progress" marker.
              let lastDoneIdx = -1;
              ordered.forEach((d, i) => {
                if (completedDeliverables.has(d.id)) lastDoneIdx = i;
              });
              const currentIdx = ordered.findIndex(
                (d, i) => i >= lastDoneIdx && !completedDeliverables.has(d.id),
              );
              return (
                <ol className="mt-3 space-y-0">
                  {ordered.map((d, idx, arr) => {
                    const done = completedDeliverables.has(d.id);
                    const isCurrent = idx === currentIdx;
                    const latestItem = latestItemByDeliverable.get(d.id);
                    return (
                      <li key={d.id} className="relative flex gap-4 pb-6 last:pb-0">
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
                              : isCurrent
                                ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200"
                                : "border bg-[hsl(var(--background))] text-[hsl(var(--muted-foreground))]"
                          }`}
                        >
                          {done ? "✓" : idx + 1}
                        </span>
                        <div className="flex-1 pt-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-medium">{d.name}</span>
                            <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                              {d.type.replaceAll("_", " ")}
                            </span>
                            {d.required ? (
                              <span className="text-xs text-red-500">Required</span>
                            ) : (
                              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                                Optional
                              </span>
                            )}
                            <span
                              className={`ml-auto text-xs font-medium ${
                                done
                                  ? "text-green-600"
                                  : isCurrent
                                    ? "text-blue-600"
                                    : "text-[hsl(var(--muted-foreground))]"
                              }`}
                            >
                              {done ? "Done" : isCurrent ? "In Progress" : "Not Started"}
                            </span>
                          </div>
                          {d.description && (
                            <p className="mt-0.5 text-sm text-[hsl(var(--muted-foreground))]">
                              {d.description}
                            </p>
                          )}
                          {/* Latest submitted asset thumbnail + provenance */}
                          {latestItem && latestItem.type === "file" && (
                            <div className="mt-2">
                              <MediaPreview
                                downloadPath={`/orgs/${orgId}/submissions/${latestSubId}/files/${latestItem.id}/download`}
                                mimeType={latestItem.mime_type}
                                fileName={latestItem.file_name}
                                className="max-h-32"
                              />
                              <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                                {latestItem.file_name}
                                {latestItem.version > 1 ? ` · v${latestItem.version}` : ""}
                              </p>
                            </div>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ol>
              );
            })()
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

        {/* Creator Assignments (instructor only) */}
        {isInstructor && (
          <div>
            <h2 className="text-xl font-semibold">Creator Assignments</h2>
            <div className="mt-3 space-y-2">
              {creators.length === 0 && (
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  No creators assigned. Assign individual creators to this project.
                </p>
              )}
              {creators.map((c) => (
                <div
                  key={c.user_id}
                  className="flex items-center justify-between rounded border px-4 py-2"
                >
                  <div>
                    <span className="text-sm font-medium">{c.user_name || c.user_id}</span>
                    <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                      Assigned {new Date(c.assigned_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeCreatorMutation.mutate(c.user_id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="User ID"
                  value={creatorUserId}
                  onChange={(e) => setCreatorUserId(e.target.value)}
                  className="flex-1 rounded border px-3 py-2 text-sm"
                />
                <Button
                  onClick={() => assignCreatorMutation.mutate()}
                  disabled={!creatorUserId.trim() || assignCreatorMutation.isPending}
                  variant="outline"
                  size="sm"
                >
                  Assign
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Peer Review */}
        <PeerReviewSection
          orgId={orgId}
          projectId={projectId}
          isInstructor={isInstructor}
        />

        {/* Submissions */}
        <div>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              {isInstructor ? "Submissions" : "My Submissions"}
            </h2>
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
                <span className="flex items-center gap-2">
                  {isInstructor && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-xs font-semibold uppercase">
                      {s.author_name?.[0] ?? "?"}
                    </span>
                  )}
                  {isInstructor && <span className="font-medium">{s.author_name}</span>}
                  <span>
                    v{s.version} — <span className="capitalize">{s.status.replaceAll("_", " ")}</span>
                  </span>
                  {s.submitted_at && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {new Date(s.submitted_at).toLocaleString()}
                    </span>
                  )}
                </span>
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
