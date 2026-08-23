"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface PackDetail {
  id: string;
  name: string;
  summary: string | null;
  description: string | null;
  status: string;
  visibility: string;
  workflow_type: string;
  difficulty: string | null;
  capability_tags: string[];
  install_count: number;
  review_status: string | null;
  rejection_reason: string | null;
  input_schema: { key: string; type: string; required: boolean }[];
  output_schema: { key: string; type: string }[];
  definition: { steps?: { id: string; type: string; name: string }[] };
}

interface Release {
  id: string;
  version: string;
  changelog: string | null;
  checksum: string;
  step_count: number;
  released_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function WorkflowPackDetailPage() {
  const { orgId, packId } = useParams<{ orgId: string; packId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [summary, setSummary] = useState<string | null>(null);
  const [visibility, setVisibility] = useState<string | null>(null);
  const [releaseVersion, setReleaseVersion] = useState("");
  const [releaseChangelog, setReleaseChangelog] = useState("");
  const [rejectReason, setRejectReason] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["workflow-pack", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: PackDetail }>(`/orgs/${orgId}/workflow-packs/${packId}`),
  });

  const { data: releasesData } = useQuery({
    queryKey: ["workflow-releases", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: Release[] }>(
        `/orgs/${orgId}/workflow-packs/${packId}/releases`,
      ),
  });

  const pack = data?.data;
  const releases = releasesData?.data ?? [];

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["workflow-pack", orgId, packId] });
    queryClient.invalidateQueries({ queryKey: ["workflow-packs", orgId] });
  };

  const updateMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiWithAuth(`/orgs/${orgId}/workflow-packs/${packId}`, {
        method: "PUT",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      invalidate();
      toast.success("Pack updated");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Update failed"),
  });

  const publishMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-packs/${packId}/releases`, {
        method: "POST",
        body: JSON.stringify({
          version: releaseVersion,
          changelog: releaseChangelog || undefined,
        }),
      }),
    onSuccess: () => {
      setReleaseVersion("");
      setReleaseChangelog("");
      invalidate();
      queryClient.invalidateQueries({ queryKey: ["workflow-releases", orgId, packId] });
      toast.success("Release published");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Publish failed"),
  });

  const reviewMutation = useMutation({
    mutationFn: (action: "submit-review" | "approve" | "reject") =>
      apiWithAuth(`/orgs/${orgId}/workflow-packs/${packId}/${action}`, {
        method: "POST",
        body: action === "reject" ? JSON.stringify({ reason: rejectReason || undefined }) : undefined,
      }),
    onSuccess: () => {
      invalidate();
      toast.success("Review status updated");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Action failed"),
  });

  const archiveMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/workflow-packs/${packId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-packs", orgId] });
      toast.success("Pack archived");
      router.replace(`/dashboard/orgs/${orgId}/workflow-packs`);
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Archive failed"),
  });

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !pack) {
    return <p className="text-sm text-red-600">Failed to load workflow pack.</p>;
  }

  const steps = pack.definition?.steps ?? [];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">{pack.name}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[pack.status] ?? ""}`}
            >
              {pack.status}
            </span>
            <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
              {pack.visibility}
            </span>
            <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
              {pack.workflow_type}
            </span>
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              {pack.install_count} install{pack.install_count !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/dashboard/orgs/${orgId}/workflow-packs/${packId}/import-comfyui`}>
            <Button size="sm" variant="secondary">Import ComfyUI</Button>
          </Link>
          <Link href={`/dashboard/orgs/${orgId}/workflow-packs/${packId}/editor`}>
            <Button size="sm">Open Editor</Button>
          </Link>
        </div>
      </div>

      {/* Metadata */}
      <section>
        <h2 className="text-xl font-semibold">Details</h2>
        <div className="mt-3 space-y-3 rounded-lg border p-4">
          <div>
            <label htmlFor="pack-summary" className="block text-sm font-medium">
              Summary
            </label>
            <Input
              id="pack-summary"
              value={summary ?? pack.summary ?? ""}
              maxLength={500}
              onChange={(e) => setSummary(e.target.value)}
              className="mt-1"
            />
          </div>
          <div className="flex items-end gap-3">
            <div>
              <label htmlFor="pack-visibility" className="block text-sm font-medium">
                Visibility
              </label>
              <select
                id="pack-visibility"
                value={visibility ?? pack.visibility}
                onChange={(e) => setVisibility(e.target.value)}
                className="mt-1 rounded-md border bg-transparent px-3 py-2 text-sm"
              >
                <option value="private">Private</option>
                <option value="unlisted">Unlisted</option>
                <option value="public">Public</option>
              </select>
            </div>
            <Button
              size="sm"
              disabled={updateMutation.isPending}
              onClick={() =>
                updateMutation.mutate({
                  summary: summary ?? undefined,
                  visibility: visibility ?? undefined,
                })
              }
            >
              Save
            </Button>
          </div>
        </div>
      </section>

      {/* I/O */}
      <section>
        <h2 className="text-xl font-semibold">Inputs &amp; Outputs</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-medium">Inputs</h3>
            {pack.input_schema.length === 0 ? (
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">None</p>
            ) : (
              <ul className="mt-2 space-y-1">
                {pack.input_schema.map((input) => (
                  <li key={input.key} className="text-sm">
                    <code className="font-mono">{input.key}</code>: {input.type}
                    {input.required ? "" : " (optional)"}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-medium">Outputs</h3>
            {pack.output_schema.length === 0 ? (
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">None</p>
            ) : (
              <ul className="mt-2 space-y-1">
                {pack.output_schema.map((output) => (
                  <li key={output.key} className="text-sm">
                    <code className="font-mono">{output.key}</code>: {output.type}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      {/* Steps */}
      <section>
        <h2 className="text-xl font-semibold">Steps ({steps.length})</h2>
        {steps.length === 0 ? (
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            No steps yet — open the editor to build the workflow.
          </p>
        ) : (
          <ol className="mt-3 space-y-1">
            {steps.map((step, i) => (
              <li key={step.id} className="rounded border px-3 py-2 text-sm">
                {i + 1}. <span className="font-medium">{step.name}</span>{" "}
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  ({step.type})
                </span>
              </li>
            ))}
          </ol>
        )}
      </section>

      {/* Releases */}
      <section>
        <h2 className="text-xl font-semibold">Releases</h2>
        <div className="mt-3 space-y-3">
          {releases.map((release) => (
            <div key={release.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <span className="font-mono font-semibold">v{release.version}</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(release.released_at).toLocaleDateString()} ·{" "}
                  {release.step_count} step{release.step_count !== 1 ? "s" : ""}
                </span>
              </div>
              {release.changelog && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  {release.changelog}
                </p>
              )}
              <p className="mt-1 font-mono text-[10px] text-[hsl(var(--muted-foreground))]">
                sha256: {release.checksum.slice(0, 16)}…
              </p>
            </div>
          ))}
          {releases.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No releases yet.</p>
          )}

          <div className="rounded-lg border border-dashed p-4">
            <h3 className="text-sm font-medium">Publish New Release</h3>
            <div className="mt-2 space-y-2">
              <Input
                value={releaseVersion}
                onChange={(e) => setReleaseVersion(e.target.value)}
                placeholder="1.0.0"
                aria-label="Release version"
                pattern="\d+\.\d+\.\d+"
              />
              <textarea
                value={releaseChangelog}
                onChange={(e) => setReleaseChangelog(e.target.value)}
                rows={2}
                maxLength={10000}
                aria-label="Changelog"
                placeholder="What changed…"
                className="block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              />
              <Button
                size="sm"
                disabled={!releaseVersion || publishMutation.isPending}
                onClick={() => publishMutation.mutate()}
              >
                {publishMutation.isPending ? "Publishing…" : "Publish Release"}
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Approval */}
      <section>
        <h2 className="text-xl font-semibold">Approval</h2>
        <div className="mt-3 rounded-lg border p-4">
          <p className="text-sm">
            Review status:{" "}
            <span className="font-medium">{pack.review_status ?? "not submitted"}</span>
          </p>
          {pack.rejection_reason && (
            <p className="mt-1 text-sm text-red-600">Reason: {pack.rejection_reason}</p>
          )}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {pack.review_status !== "pending" && pack.review_status !== "approved" && (
              <Button
                size="sm"
                variant="secondary"
                disabled={reviewMutation.isPending}
                onClick={() => reviewMutation.mutate("submit-review")}
              >
                Submit for Review
              </Button>
            )}
            {pack.review_status === "pending" && (
              <>
                <Button
                  size="sm"
                  disabled={reviewMutation.isPending}
                  onClick={() => reviewMutation.mutate("approve")}
                >
                  Approve
                </Button>
                <Input
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Rejection reason"
                  aria-label="Rejection reason"
                  className="w-56"
                />
                <Button
                  size="sm"
                  variant="secondary"
                  disabled={reviewMutation.isPending}
                  onClick={() => reviewMutation.mutate("reject")}
                >
                  Reject
                </Button>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Danger zone */}
      <section>
        <h2 className="text-xl font-semibold text-red-600">Danger Zone</h2>
        <div className="mt-3 rounded-lg border border-red-200 p-4 dark:border-red-900">
          <Button
            size="sm"
            variant="secondary"
            disabled={archiveMutation.isPending}
            onClick={() => {
              if (window.confirm("Archive this workflow pack?")) {
                archiveMutation.mutate();
              }
            }}
          >
            Archive Pack
          </Button>
        </div>
      </section>
    </div>
  );
}
