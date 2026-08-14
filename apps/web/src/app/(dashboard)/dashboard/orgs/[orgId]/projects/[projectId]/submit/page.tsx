"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface Deliverable {
  id: string;
  name: string;
  type: string;
  required: boolean;
}

export default function SubmitPage() {
  const { orgId, projectId } = useParams<{ orgId: string; projectId: string }>();
  const router = useRouter();

  const { data: projectData } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () =>
      apiWithAuth<{ data: { deliverables: Deliverable[] } }>(`/orgs/${orgId}/projects/${projectId}`),
  });

  const deliverables = projectData?.data?.deliverables ?? [];
  const [textInputs, setTextInputs] = useState<Record<string, string>>({});
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
    onSuccess: () => router.push(`/dashboard/orgs/${orgId}/projects/${projectId}`),
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to submit"),
  });

  if (!submissionId) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <h1 className="text-3xl font-bold">New Submission</h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Create a draft submission, then upload your deliverables.
        </p>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button onClick={() => createDraft.mutate()} disabled={createDraft.isPending}>
          {createDraft.isPending ? "Creating..." : "Start Draft"}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Upload Deliverables</h1>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="space-y-4">
        {deliverables.map((d) => (
          <div key={d.id} className="rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium">{d.name}</h3>
              {d.required && <span className="text-xs text-red-500">Required</span>}
            </div>
            <p className="mt-1 text-xs capitalize text-[hsl(var(--muted-foreground))]">{d.type}</p>

            {d.type === "file" && (
              <input
                type="file"
                className="mt-3 block w-full text-sm"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  const formData = new FormData();
                  formData.append("file", file);
                  formData.append("deliverable_id", d.id);
                  try {
                    const token = useAuthStore.getState().accessToken;
                    await fetch(`/api/v1/orgs/${orgId}/submissions/${submissionId}/files`, {
                      method: "POST",
                      body: formData,
                      credentials: "include",
                      headers: token ? { Authorization: `Bearer ${token}` } : {},
                    });
                  } catch {
                    setError("File upload failed");
                  }
                }}
              />
            )}

            {(d.type === "text" || d.type === "markdown") && (
              <textarea
                className="mt-3 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
                rows={4}
                placeholder={`Enter ${d.name}...`}
                value={textInputs[d.id] ?? ""}
                onChange={(e) => setTextInputs({ ...textInputs, [d.id]: e.target.value })}
              />
            )}

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
        ))}
      </div>

      <Button
        onClick={async () => {
          // Save text/link items before submitting
          for (const [delivId, content] of Object.entries(textInputs)) {
            if (content.trim()) {
              try {
                await apiWithAuth(
                  `/orgs/${orgId}/submissions/${submissionId}/items`,
                  {
                    method: "POST",
                    body: JSON.stringify({ deliverable_id: delivId, content }),
                  },
                );
              } catch {
                setError(`Failed to save content for deliverable.`);
                return;
              }
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
