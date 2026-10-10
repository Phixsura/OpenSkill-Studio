"use client";

// Sync console (ADR-018 §10/§11): sync profiles, run history with
// cursor/stats, record-level conflicts, roster provisioning trigger.

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface SyncProfile {
  id: string;
  connection_id: string;
  name: string;
  model: string;
  direction: string;
  schedule: string;
  enabled: boolean;
}

interface SyncRun {
  id: string;
  profile_id: string;
  status: string;
  trigger: string;
  stats: Record<string, number>;
  error: { class?: string } | null;
  started_at: string | null;
  finished_at: string | null;
}

interface RecordResult {
  id: string;
  external_id: string;
  model: string;
  outcome: string;
  conflict_class: string | null;
  detail: Record<string, unknown>;
}

const RUN_COLORS: Record<string, string> = {
  succeeded: "bg-green-100 text-green-800",
  partial: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
  running: "bg-blue-100 text-blue-800",
  queued: "bg-gray-100 text-gray-800",
  cancelled: "bg-gray-100 text-gray-800",
};

export default function SyncIntegrationsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const base = `/orgs/${orgId}/integrations`;

  const [openRun, setOpenRun] = useState<string | null>(null);

  const profilesQ = useQuery({
    queryKey: ["intg-sync-profiles", orgId],
    queryFn: () => apiWithAuth<{ data: SyncProfile[] }>(`${base}/sync-profiles`),
  });
  const runsQ = useQuery({
    queryKey: ["intg-sync-runs", orgId],
    queryFn: () => apiWithAuth<{ data: SyncRun[] }>(`${base}/sync-runs`),
  });
  const conflictsQ = useQuery({
    queryKey: ["intg-run-records", orgId, openRun],
    queryFn: () =>
      apiWithAuth<{ data: RecordResult[] }>(
        `${base}/sync-runs/${openRun}/records?outcome=conflict`,
      ),
    enabled: openRun !== null,
  });

  const onError = (err: unknown) =>
    toast.error(err instanceof ApiError ? err.message : "Request failed");

  const runNow = useMutation({
    mutationFn: (args: { id: string; backfill: boolean }) =>
      apiWithAuth(`${base}/sync-profiles/${args.id}/run?backfill=${args.backfill}`, {
        method: "POST",
      }),
    onSuccess: () => {
      toast.success("Run queued");
      queryClient.invalidateQueries({ queryKey: ["intg-sync-runs", orgId] });
    },
    onError,
  });

  const provisionRoster = useMutation({
    mutationFn: (connectionId: string) =>
      apiWithAuth<{ data: Record<string, number> }>(
        `${base}/connections/${connectionId}/provision-roster`,
        { method: "POST", body: JSON.stringify({}) },
      ),
    onSuccess: (res) => {
      const r = res.data;
      toast.success(
        `Provisioned: ${r.cohorts_created} cohorts, ${r.members_added} members, ${r.conflicts} conflicts`,
      );
      queryClient.invalidateQueries({ queryKey: ["intg-sync-runs", orgId] });
    },
    onError,
  });

  const profiles = profilesQ.data?.data ?? [];
  const runs = runsQ.data?.data ?? [];

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Sync</h1>
        <p className="text-muted-foreground text-sm">
          Pull/push profiles with destination-confirmed cursors. Conflicts are skipped, never
          guessed — resolve them here and re-run.
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Profiles</h2>
        {profilesQ.isLoading && <p>Loading profiles…</p>}
        {profiles.length === 0 && !profilesQ.isLoading && (
          <p className="text-muted-foreground text-sm">
            No sync profiles. Create one via the API for your connection.
          </p>
        )}
        <ul className="space-y-2">
          {profiles.map((p) => (
            <li
              key={p.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
            >
              <div>
                <span className="font-medium">{p.name}</span>
                <span className="ml-2 font-mono text-xs">{p.model}</span>
                <span className="text-muted-foreground ml-2 text-xs">
                  {p.direction} · {p.schedule}
                </span>
                {!p.enabled && <span className="ml-2 text-xs text-red-700">disabled</span>}
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => runNow.mutate({ id: p.id, backfill: false })}>
                  Run
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => runNow.mutate({ id: p.id, backfill: true })}
                >
                  Backfill
                </Button>
                {p.model.startsWith("roster.") && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => provisionRoster.mutate(p.connection_id)}
                  >
                    Provision roster
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Runs</h2>
        {runsQ.isLoading && <p>Loading runs…</p>}
        <ul className="space-y-2">
          {runs.map((r) => (
            <li key={r.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-sm">
                  <span className={`rounded px-2 py-0.5 text-xs ${RUN_COLORS[r.status] ?? ""}`}>
                    {r.status}
                  </span>
                  <span className="text-muted-foreground ml-2 text-xs">{r.trigger}</span>
                  <span className="ml-2 font-mono text-xs">
                    {Object.entries(r.stats ?? {})
                      .filter(([, v]) => typeof v === "number" && v > 0)
                      .map(([k, v]) => `${k}:${v}`)
                      .join(" ")}
                  </span>
                  {r.error?.class && (
                    <span className="ml-2 text-xs text-red-700">{r.error.class}</span>
                  )}
                </div>
                {(r.stats?.conflicts ?? 0) > 0 && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOpenRun(openRun === r.id ? null : r.id)}
                  >
                    Conflicts
                  </Button>
                )}
              </div>
              {openRun === r.id && (
                <ul className="mt-2 space-y-1 border-t pt-2 text-xs">
                  {(conflictsQ.data?.data ?? []).map((c) => (
                    <li key={c.id} className="font-mono">
                      {c.external_id} — {c.conflict_class}
                      {Object.keys(c.detail ?? {}).length > 0 && (
                        <span className="text-muted-foreground"> {JSON.stringify(c.detail)}</span>
                      )}
                    </li>
                  ))}
                  {(conflictsQ.data?.data ?? []).length === 0 && <li>No conflict rows.</li>}
                </ul>
              )}
            </li>
          ))}
          {runs.length === 0 && !runsQ.isLoading && (
            <li className="text-muted-foreground text-sm">No runs yet.</li>
          )}
        </ul>
      </section>
    </div>
  );
}
