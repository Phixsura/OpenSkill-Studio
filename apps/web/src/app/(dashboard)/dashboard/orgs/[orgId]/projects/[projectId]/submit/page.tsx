"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MediaPreview } from "@/components/media-preview";
import { GenerationData, type GenerationMeta } from "@/components/generation-data";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface Deliverable {
  id: string;
  name: string;
  description: string | null;
  type: string;
  required: boolean;
  config: {
    accepted_formats?: string[];
    max_files?: number;
    max_file_size_mb?: number;
  };
  sort_order: number;
}

interface UploadedItem {
  id: string;
  file_name: string | null;
  mime_type: string | null;
  version: number;
  generation?: GenerationMeta | null;
}

interface PromptFormState {
  prompt: string;
  negative_prompt: string;
  tool: string;
  model: string;
  seed: string;
  cfg_scale: string;
  steps: string;
  sampler: string;
  parameters: string;
  notes: string;
}

const EMPTY_PROMPT_FORM: PromptFormState = {
  prompt: "",
  negative_prompt: "",
  tool: "",
  model: "",
  seed: "",
  cfg_scale: "",
  steps: "",
  sampler: "",
  parameters: "",
  notes: "",
};

const MEDIA_TYPES = new Set(["image", "video", "audio", "reference", "final_output", "file"]);

const DEFAULT_ACCEPT: Record<string, string> = {
  image: "image/png,image/jpeg,image/webp,image/gif",
  video: "video/mp4,video/webm",
  audio: "audio/mpeg,audio/wav,audio/mp4,audio/x-m4a",
  reference: "image/*,video/*,audio/*,application/pdf",
  final_output: "image/*,video/*,audio/*,application/pdf",
  file: "",
};

export default function SubmitPage() {
  const { orgId, projectId } = useParams<{ orgId: string; projectId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: projectData, isLoading: projectLoading, isError: projectError } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () =>
      apiWithAuth<{ data: { title: string; project_type: string; deliverables: Deliverable[] } }>(
        `/orgs/${orgId}/projects/${projectId}`,
      ),
  });

  const project = projectData?.data;
  const deliverables = [...(project?.deliverables ?? [])].sort(
    (a, b) => a.sort_order - b.sort_order,
  );

  const [textInputs, setTextInputs] = useState<Record<string, string>>({});
  const [promptInputs, setPromptInputs] = useState<Record<string, PromptFormState>>({});
  const [uploaded, setUploaded] = useState<Record<string, UploadedItem[]>>({});
  const [uploading, setUploading] = useState<Record<string, boolean>>({});
  // Optional "what changed" note attached to the next upload of a deliverable
  const [versionNotes, setVersionNotes] = useState<Record<string, string>>({});
  const [savedPrompts, setSavedPrompts] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [submissionId, setSubmissionId] = useState<string | null>(null);

  const createDraft = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { id: string } }>(`/orgs/${orgId}/projects/${projectId}/submissions`, {
        method: "POST",
      }),
    onSuccess: (res) => setSubmissionId(res.data.id),
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to create draft"),
  });

  const submitDraft = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}/submit`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions", projectId] });
      router.push(`/dashboard/orgs/${orgId}/projects/${projectId}`);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to submit"),
  });

  const handleFileUpload = async (d: Deliverable, file: File) => {
    setError(null);

    // Client-side pre-checks for friendlier errors
    const maxMb = d.config?.max_file_size_mb ?? 50;
    if (file.size > maxMb * 1024 * 1024) {
      setError(`"${file.name}" exceeds the ${maxMb}MB limit for ${d.name}.`);
      return;
    }
    const accepted = d.config?.accepted_formats;
    if (accepted?.length && !accepted.includes(file.type)) {
      setError(`"${file.type || "unknown type"}" is not accepted for ${d.name}. Allowed: ${accepted.join(", ")}`);
      return;
    }

    setUploading((u) => ({ ...u, [d.id]: true }));
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("deliverable_id", d.id);
      const note = versionNotes[d.id]?.trim();
      if (note) formData.append("note", note);
      const token = useAuthStore.getState().accessToken;
      const res = await fetch(`/api/v1/orgs/${orgId}/submissions/${submissionId}/files`, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.error?.message ?? body?.detail ?? `Upload failed (${res.status})`);
      }
      const body = await res.json();
      // Parse extracted generation metadata, if the server found any
      let generation: GenerationMeta | null = null;
      if (body.data.content) {
        try {
          generation = JSON.parse(body.data.content)?.generation ?? null;
        } catch {
          generation = null;
        }
      }
      const item: UploadedItem = {
        id: body.data.id,
        file_name: body.data.file_name ?? file.name,
        mime_type: body.data.mime_type ?? file.type,
        version: body.data.version ?? 1,
        generation,
      };
      setUploaded((prev) => ({ ...prev, [d.id]: [...(prev[d.id] ?? []), item] }));
      setVersionNotes((n) => ({ ...n, [d.id]: "" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "File upload failed");
    } finally {
      setUploading((u) => ({ ...u, [d.id]: false }));
    }
  };

  const handlePromptSave = async (d: Deliverable) => {
    setError(null);
    const p = promptInputs[d.id];
    if (!p?.prompt?.trim()) {
      setError(`Please enter a prompt for ${d.name}.`);
      return;
    }
    let parameters: Record<string, unknown> | undefined;
    if (p.parameters?.trim()) {
      try {
        parameters = JSON.parse(p.parameters);
      } catch {
        setError("Parameters must be valid JSON (e.g. {\"aspect_ratio\": \"9:16\"}).");
        return;
      }
    }
    const seed = p.seed?.trim() ? parseInt(p.seed, 10) : undefined;
    const cfgScale = p.cfg_scale?.trim() ? parseFloat(p.cfg_scale) : undefined;
    const steps = p.steps?.trim() ? parseInt(p.steps, 10) : undefined;
    if (seed !== undefined && Number.isNaN(seed)) {
      setError("Seed must be a number.");
      return;
    }
    try {
      await apiWithAuth(`/orgs/${orgId}/submissions/${submissionId}/prompt-items`, {
        method: "POST",
        body: JSON.stringify({
          deliverable_id: d.id,
          prompt: p.prompt.trim(),
          negative_prompt: p.negative_prompt?.trim() || undefined,
          tool: p.tool?.trim() || undefined,
          model: p.model?.trim() || undefined,
          seed,
          cfg_scale: cfgScale !== undefined && !Number.isNaN(cfgScale) ? cfgScale : undefined,
          steps: steps !== undefined && !Number.isNaN(steps) ? steps : undefined,
          sampler: p.sampler?.trim() || undefined,
          parameters,
          notes: p.notes?.trim() || undefined,
        }),
      });
      setSavedPrompts((s) => ({ ...s, [d.id]: true }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save prompt");
    }
  };

  /** Civitai-Remix semantics for teaching: prefill the prompt form from
   * generation metadata extracted from an uploaded image. */
  const fillPromptFromMeta = (meta: GenerationMeta) => {
    const promptDeliverable = deliverables.find((d) => d.type === "prompt");
    if (!promptDeliverable) return;
    setPromptInputs((prev) => ({
      ...prev,
      [promptDeliverable.id]: {
        ...EMPTY_PROMPT_FORM,
        ...prev[promptDeliverable.id],
        prompt: meta.prompt ?? prev[promptDeliverable.id]?.prompt ?? "",
        negative_prompt: meta.negative_prompt ?? "",
        model: meta.model ?? prev[promptDeliverable.id]?.model ?? "",
        seed: meta.seed != null ? String(meta.seed) : "",
        cfg_scale: meta.cfg_scale != null ? String(meta.cfg_scale) : "",
        steps: meta.steps != null ? String(meta.steps) : "",
        sampler: meta.sampler ?? "",
      },
    }));
    setSavedPrompts((s) => ({ ...s, [promptDeliverable.id]: false }));
  };

  if (projectLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading project...</p>;
  if (projectError) return <p className="text-sm text-red-600">Failed to load project. Please try again.</p>;

  if (!submissionId) {
    const requiredCount = deliverables.filter((d) => d.required).length;
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold">New Submission</h1>
          {project?.title && (
            <p className="mt-1 text-[hsl(var(--muted-foreground))]">{project.title}</p>
          )}
        </div>

        {/* Preview the work ahead before the learner commits to a draft */}
        {deliverables.length > 0 && (
          <div className="rounded-lg border p-4">
            <p className="text-sm font-semibold">
              What you&apos;ll submit
              <span className="ml-2 font-normal text-[hsl(var(--muted-foreground))]">
                {deliverables.length} deliverable{deliverables.length !== 1 ? "s" : ""}
                {requiredCount > 0 ? ` · ${requiredCount} required` : ""}
              </span>
            </p>
            <ol className="mt-3 space-y-2">
              {deliverables.map((d, i) => (
                <li key={d.id} className="flex items-center gap-3 text-sm">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-xs font-medium">
                    {i + 1}
                  </span>
                  <span className="font-medium">{d.name}</span>
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                    {d.type.replace("_", " ")}
                  </span>
                  {d.required ? (
                    <span className="text-xs text-red-600">Required</span>
                  ) : (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">Optional</span>
                  )}
                </li>
              ))}
            </ol>
          </div>
        )}

        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Starting a draft lets you save work in progress — nothing is sent for review until you
          press Submit.
        </p>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button onClick={() => createDraft.mutate()} disabled={createDraft.isPending}>
          {createDraft.isPending ? "Creating..." : "Start Draft"}
        </Button>
      </div>
    );
  }

  const isWorkflow = project?.project_type === "ai_visual";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-3xl font-bold">
        {isWorkflow ? "Production Workflow" : "Upload Deliverables"}
      </h1>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="space-y-4">
        {deliverables.map((d, idx) => {
          const items = uploaded[d.id] ?? [];
          const latest = items[items.length - 1];
          const done =
            items.length > 0 || savedPrompts[d.id] || (textInputs[d.id]?.trim()?.length ?? 0) > 0;

          return (
            <div key={d.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {isWorkflow && (
                    <span
                      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                        done
                          ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200"
                          : "bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))]"
                      }`}
                    >
                      {done ? "✓" : idx + 1}
                    </span>
                  )}
                  <h3 className="font-medium">{d.name}</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                    {d.type.replace("_", " ")}
                  </span>
                  {d.required && <span className="text-xs text-red-500">Required</span>}
                </div>
              </div>
              {d.description && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{d.description}</p>
              )}

              {/* Media / file upload */}
              {MEDIA_TYPES.has(d.type) && (
                <div className="mt-3 space-y-3">
                  <input
                    type="file"
                    accept={
                      d.config?.accepted_formats?.join(",") || DEFAULT_ACCEPT[d.type] || undefined
                    }
                    disabled={uploading[d.id]}
                    className="block w-full text-sm"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(d, file);
                      e.target.value = "";
                    }}
                  />
                  {latest && (
                    <input
                      type="text"
                      placeholder="What changed in this version? (optional note)"
                      value={versionNotes[d.id] ?? ""}
                      onChange={(e) =>
                        setVersionNotes((n) => ({ ...n, [d.id]: e.target.value }))
                      }
                      className="block w-full rounded-md border px-2 py-1 text-xs"
                    />
                  )}
                  {uploading[d.id] && (
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Uploading…</p>
                  )}

                  {latest && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium">{latest.file_name}</span>
                        {latest.version > 1 && (
                          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-200">
                            v{latest.version}
                          </span>
                        )}
                      </div>
                      <MediaPreview
                        downloadPath={`/orgs/${orgId}/submissions/${submissionId}/files/${latest.id}/download`}
                        mimeType={latest.mime_type}
                        fileName={latest.file_name}
                      />
                      {latest.generation && (
                        <div className="space-y-1.5">
                          <GenerationData meta={latest.generation} />
                          {deliverables.some((x) => x.type === "prompt") && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => fillPromptFromMeta(latest.generation!)}
                            >
                              ✨ Fill prompt form from this image
                            </Button>
                          )}
                        </div>
                      )}
                      {items.length > 1 && (
                        <details className="text-xs text-[hsl(var(--muted-foreground))]">
                          <summary className="cursor-pointer">
                            Version history ({items.length} versions)
                          </summary>
                          <ul className="mt-1 space-y-0.5 pl-4">
                            {[...items].reverse().map((it) => (
                              <li key={it.id}>
                                v{it.version} — {it.file_name}
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">
                        Upload again to replace (previous versions are kept).
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Prompt form (industry fields: negative/seed/cfg/steps/sampler) */}
              {d.type === "prompt" &&
                (() => {
                  const form = promptInputs[d.id] ?? EMPTY_PROMPT_FORM;
                  const set = (field: keyof PromptFormState) => (
                    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
                  ) =>
                    setPromptInputs((p) => ({
                      ...p,
                      [d.id]: { ...(p[d.id] ?? EMPTY_PROMPT_FORM), [field]: e.target.value },
                    }));
                  return (
                    <div className="mt-3 space-y-2">
                      {savedPrompts[d.id] ? (
                        <p className="text-sm text-green-600">✓ Prompt saved</p>
                      ) : (
                        <>
                          <textarea
                            className="block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-sm"
                            rows={4}
                            maxLength={10000}
                            placeholder="Your generation prompt..."
                            value={form.prompt}
                            onChange={set("prompt")}
                          />
                          <textarea
                            className="block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-sm"
                            rows={2}
                            maxLength={10000}
                            placeholder="Negative prompt (optional)"
                            value={form.negative_prompt}
                            onChange={set("negative_prompt")}
                          />
                          <div className="grid gap-2 sm:grid-cols-2">
                            <Input
                              placeholder="Tool (e.g. Seedream)"
                              value={form.tool}
                              onChange={set("tool")}
                            />
                            <Input
                              placeholder="Model (optional)"
                              value={form.model}
                              onChange={set("model")}
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                            <Input
                              placeholder="Seed"
                              inputMode="numeric"
                              value={form.seed}
                              onChange={set("seed")}
                            />
                            <Input
                              placeholder="CFG"
                              inputMode="decimal"
                              value={form.cfg_scale}
                              onChange={set("cfg_scale")}
                            />
                            <Input
                              placeholder="Steps"
                              inputMode="numeric"
                              value={form.steps}
                              onChange={set("steps")}
                            />
                            <Input
                              placeholder="Sampler"
                              value={form.sampler}
                              onChange={set("sampler")}
                            />
                          </div>
                          <Input
                            placeholder='Extra parameters JSON, e.g. {"aspect_ratio": "9:16"} (optional)'
                            value={form.parameters}
                            onChange={set("parameters")}
                          />
                          <Input
                            placeholder="Notes (optional)"
                            value={form.notes}
                            onChange={set("notes")}
                          />
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => handlePromptSave(d)}
                          >
                            Save Prompt
                          </Button>
                        </>
                      )}
                    </div>
                  );
                })()}

              {/* Text / markdown */}
              {(d.type === "text" || d.type === "markdown") && (
                <textarea
                  className="mt-3 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
                  rows={4}
                  placeholder={`Enter ${d.name}...`}
                  value={textInputs[d.id] ?? ""}
                  onChange={(e) => setTextInputs({ ...textInputs, [d.id]: e.target.value })}
                />
              )}

              {/* Link */}
              {d.type === "link" && (
                <Input
                  type="url"
                  placeholder="https://..."
                  className="mt-3"
                  value={textInputs[d.id] ?? ""}
                  onChange={(e) => setTextInputs({ ...textInputs, [d.id]: e.target.value })}
                />
              )}
            </div>
          );
        })}
      </div>

      <Button
        onClick={async () => {
          // Save text/link items via the submission update endpoint
          const items = Object.entries(textInputs)
            .filter(([, content]) => content.trim())
            .map(([delivId, content]) => ({
              deliverable_id: delivId,
              content: content.trim(),
              // Preserve the deliverable's declared format so markdown renders as markdown
              type: deliverables.find((d) => d.id === delivId)?.type === "markdown" ? "markdown" : "text",
            }));

          if (items.length > 0) {
            try {
              await apiWithAuth(
                `/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}`,
                {
                  method: "PUT",
                  body: JSON.stringify({ items }),
                },
              );
            } catch {
              setError("Failed to save deliverable content.");
              return;
            }
          }
          submitDraft.mutate();
        }}
        disabled={submitDraft.isPending}
      >
        {submitDraft.isPending ? "Submitting..." : "Submit"}
      </Button>
    </div>
  );
}
