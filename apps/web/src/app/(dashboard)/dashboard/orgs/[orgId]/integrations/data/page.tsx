"use client";

// Data tooling (ADR-018 §16): bulk CSV imports (dry-run first, commit after
// preview) and governed warehouse export streams.

import { useRef, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, apiWithAuth } from "@/lib/api";

interface ImportJob {
  id: string;
  kind: string;
  mode: string;
  status: string;
  dry_stats: Record<string, number>;
  stats: Record<string, number>;
}

interface ExportStream {
  id: string;
  name: string;
  dataset: string;
  field_allowlist: string[];
  schedule: string;
  cursor: Record<string, unknown>;
}

interface ExportRun {
  id: string;
  status: string;
  row_count: number;
  manifest_key: string | null;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function DataIntegrationsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const base = `/orgs/${orgId}/integrations`;

  const fileRef = useRef<HTMLInputElement>(null);
  const [mode, setMode] = useState("partial");
  const [job, setJob] = useState<ImportJob | null>(null);
  const [streamName, setStreamName] = useState("");
  const [dataset, setDataset] = useState("events");
  const [openStream, setOpenStream] = useState<string | null>(null);

  const streamsQ = useQuery({
    queryKey: ["intg-export-streams", orgId],
    queryFn: () => apiWithAuth<{ data: ExportStream[] }>(`${base}/export-streams`),
  });
  const runsQ = useQuery({
    queryKey: ["intg-export-runs", orgId, openStream],
    queryFn: () => apiWithAuth<{ data: ExportRun[] }>(`${base}/export-streams/${openStream}/runs`),
    enabled: openStream !== null,
  });

  const onError = (err: unknown) =>
    toast.error(err instanceof ApiError ? err.message : "Request failed");

  const upload = useMutation({
    mutationFn: async () => {
      const file = fileRef.current?.files?.[0];
      if (!file) throw new ApiError(0, "NO_FILE", "Choose a CSV file first");
      const form = new FormData();
      form.append("kind", "users");
      form.append("mode", mode);
      form.append("file", file);
      // multipart upload: bypass the JSON helper but reuse the live token
      // (sharedRefresh would force a rotation per upload — wrong tool).
      const { useAuthStore } = await import("@/stores/auth");
      const token = useAuthStore.getState().accessToken ?? "";
      const res = await fetch(`${API_BASE}/api/v1${base}/imports`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const body = await res.json();
      if (!res.ok) {
        throw new ApiError(
          res.status,
          body?.error?.code ?? "IMPORT_FAILED",
          body?.error?.message ?? "Upload failed",
        );
      }
      return body as { data: ImportJob };
    },
    onSuccess: (res) => {
      setJob(res.data);
      toast.success("Previewed — review the dry-run stats, then commit");
    },
    onError,
  });

  const commit = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth<{ data: ImportJob }>(`${base}/imports/${id}/commit`, { method: "POST" }),
    onSuccess: (res) => {
      setJob(res.data);
      toast.success(`Import ${res.data.status}`);
    },
    onError,
  });

  const createStream = useMutation({
    mutationFn: () =>
      apiWithAuth(`${base}/export-streams`, {
        method: "POST",
        body: JSON.stringify({ name: streamName, dataset }),
      }),
    onSuccess: () => {
      toast.success("Export stream created");
      setStreamName("");
      queryClient.invalidateQueries({ queryKey: ["intg-export-streams", orgId] });
    },
    onError,
  });

  // A bare <a href> to the authenticated errors.csv endpoint 401s (no
  // bearer in browser navigation) — fetch with auth and hand over a blob.
  const downloadErrors = async (jobId: string) => {
    try {
      const { apiTextWithAuth } = await import("@/lib/api");
      const csv = await apiTextWithAuth(`${base}/imports/${jobId}/errors.csv`);
      const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `import-${jobId}-errors.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      onError(err);
    }
  };

  const runStream = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth<{ data: ExportRun }>(`${base}/export-streams/${id}/run`, {
        method: "POST",
      }),
    onSuccess: (res) => {
      toast.success(`Export ${res.data.status}: ${res.data.row_count} rows`);
      queryClient.invalidateQueries({ queryKey: ["intg-export-runs", orgId] });
    },
    onError,
  });

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Data</h1>
        <p className="text-muted-foreground text-sm">
          Imports preview before committing; exports carry only allowlisted fields.
        </p>
      </div>

      <section className="space-y-3 rounded-lg border p-4">
        <h2 className="text-lg font-medium">Bulk import (users CSV)</h2>
        <div className="flex flex-wrap items-center gap-3">
          <input aria-label="CSV file" ref={fileRef} type="file" accept=".csv,text/csv" />
          <select
            aria-label="Import mode"
            className="rounded-md border px-2 py-1 text-sm"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="partial">partial (apply valid rows)</option>
            <option value="atomic">atomic (all or nothing)</option>
          </select>
          <Button disabled={upload.isPending} onClick={() => upload.mutate()}>
            Upload & preview
          </Button>
        </div>
        {job && (
          <div className="rounded-md border p-3 text-sm">
            <div>
              Status: <span className="font-medium">{job.status}</span> ({job.mode})
            </div>
            <div className="font-mono text-xs">
              dry-run — valid: {job.dry_stats?.valid ?? 0}, errors: {job.dry_stats?.errors ?? 0},
              creates: {job.dry_stats?.creates ?? 0}, updates: {job.dry_stats?.updates ?? 0}
            </div>
            {Object.keys(job.stats ?? {}).length > 0 && (
              <div className="font-mono text-xs">
                committed — applied: {job.stats?.applied ?? 0}, errors: {job.stats?.errors ?? 0}
              </div>
            )}
            <div className="mt-2 flex gap-2">
              {job.status === "previewed" && (
                <Button size="sm" disabled={commit.isPending} onClick={() => commit.mutate(job.id)}>
                  Commit
                </Button>
              )}
              {(job.dry_stats?.errors ?? 0) > 0 && (
                <Button size="sm" variant="outline" onClick={() => downloadErrors(job.id)}>
                  Download error report
                </Button>
              )}
            </div>
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Export streams</h2>
        <ul className="space-y-2">
          {(streamsQ.data?.data ?? []).map((s) => (
            <li key={s.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-medium">{s.name}</span>
                  <span className="ml-2 font-mono text-xs">{s.dataset}</span>
                  <span className="text-muted-foreground ml-2 text-xs">
                    fields: {s.field_allowlist.join(", ")}
                  </span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => runStream.mutate(s.id)}>
                    Run export
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOpenStream(openStream === s.id ? null : s.id)}
                  >
                    Runs
                  </Button>
                </div>
              </div>
              {openStream === s.id && (
                <ul className="mt-2 space-y-1 border-t pt-2 text-xs">
                  {(runsQ.data?.data ?? []).map((r) => (
                    <li key={r.id} className="font-mono">
                      {r.created_at} — {r.status}, {r.row_count} rows
                      {r.manifest_key && <span> → {r.manifest_key}</span>}
                    </li>
                  ))}
                  {(runsQ.data?.data ?? []).length === 0 && <li>No runs yet.</li>}
                </ul>
              )}
            </li>
          ))}
          {(streamsQ.data?.data ?? []).length === 0 && !streamsQ.isLoading && (
            <li className="text-muted-foreground text-sm">No export streams.</li>
          )}
        </ul>
        <div className="flex flex-wrap items-end gap-2">
          <Input
            aria-label="Stream name"
            className="max-w-xs"
            placeholder="nightly-events"
            value={streamName}
            onChange={(e) => setStreamName(e.target.value)}
          />
          <select
            aria-label="Dataset"
            className="rounded-md border px-2 py-1 text-sm"
            value={dataset}
            onChange={(e) => setDataset(e.target.value)}
          >
            <option value="events">events</option>
            <option value="enrollments">enrollments</option>
          </select>
          <Button
            disabled={!streamName || createStream.isPending}
            onClick={() => createStream.mutate()}
          >
            Create stream
          </Button>
        </div>
      </section>
    </div>
  );
}
