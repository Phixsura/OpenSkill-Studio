"use client";

// Sync console (ADR-018 §10/§11): sync profiles, run history with
// cursor/stats, record-level conflicts, roster provisioning trigger.

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface MappingProfile {
  id: string;
  name: string;
  direction: string;
  model: string;
  document: { fields?: unknown[] };
  version: number;
}

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
  resolved_action: string | null;
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
  const [mapName, setMapName] = useState("");
  const [mapModel, setMapModel] = useState("roster.class");
  const [mapDoc, setMapDoc] = useState(
    JSON.stringify({ fields: [{ target: "title", path: "title" }] }, null, 2),
  );
  const [previewFor, setPreviewFor] = useState<string | null>(null);
  const [sampleJson, setSampleJson] = useState('{"title": "Example"}');
  const [previewOut, setPreviewOut] = useState<string | null>(null);

  const profilesQ = useQuery({
    queryKey: ["intg-sync-profiles", orgId],
    queryFn: () => apiWithAuth<{ data: SyncProfile[] }>(`${base}/sync-profiles`),
  });
  const runsQ = useQuery({
    queryKey: ["intg-sync-runs", orgId],
    queryFn: () => apiWithAuth<{ data: SyncRun[] }>(`${base}/sync-runs`),
  });
  const mappingsQ = useQuery({
    queryKey: ["intg-mappings", orgId],
    queryFn: () => apiWithAuth<{ data: MappingProfile[] }>(`${base}/mapping-profiles`),
  });
  const conflictsQ = useQuery({
    queryKey: ["intg-run-records", orgId, openRun],
    queryFn: () =>
      apiWithAuth<{ data: RecordResult[] }>(
        `${base}/sync-runs/${openRun}/records?outcome=conflict`,
      ),
    enabled: openRun !== null,
  });

  const resolveConflict = useMutation({
    mutationFn: ({ resultId, action }: { resultId: string; action: string }) =>
      apiWithAuth(`${base}/sync-runs/${openRun}/records/${resultId}/resolve`, {
        method: "POST",
        body: JSON.stringify({ action }),
      }),
    onSuccess: () => {
      toast.success("Conflict resolved");
      queryClient.invalidateQueries({ queryKey: ["intg-run-records", orgId, openRun] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Resolve failed"),
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

  const createMapping = useMutation({
    mutationFn: () => {
      let document: unknown;
      try {
        document = JSON.parse(mapDoc);
      } catch {
        throw new ApiError(0, "BAD_JSON", "Mapping document is not valid JSON");
      }
      return apiWithAuth(`${base}/mapping-profiles`, {
        method: "POST",
        body: JSON.stringify({
          name: mapName,
          direction: "inbound",
          model: mapModel,
          document,
        }),
      });
    },
    onSuccess: () => {
      toast.success("Mapping created");
      setMapName("");
      queryClient.invalidateQueries({ queryKey: ["intg-mappings", orgId] });
    },
    onError,
  });

  const previewMapping = useMutation({
    mutationFn: (id: string) => {
      let sample: unknown;
      try {
        sample = JSON.parse(sampleJson);
      } catch {
        throw new ApiError(0, "BAD_JSON", "Sample is not valid JSON");
      }
      return apiWithAuth<{ data: unknown[] }>(`${base}/mapping-profiles/${id}/preview`, {
        method: "POST",
        body: JSON.stringify({ samples: [sample] }),
      });
    },
    onSuccess: (res) => setPreviewOut(JSON.stringify(res.data[0], null, 2)),
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
        <h2 className="text-lg font-medium">Mapping profiles</h2>
        <ul className="space-y-2">
          {(mappingsQ.data?.data ?? []).map((m) => (
            <li key={m.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-medium">{m.name}</span>
                  <span className="ml-2 font-mono text-xs">{m.model}</span>
                  <span className="text-muted-foreground ml-2 text-xs">
                    v{m.version} · {m.direction} · {(m.document.fields ?? []).length} fields
                  </span>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setPreviewFor(previewFor === m.id ? null : m.id)}
                >
                  Preview
                </Button>
              </div>
              {previewFor === m.id && (
                <div className="mt-2 space-y-2 border-t pt-2">
                  <textarea
                    aria-label={`Sample record for ${m.name}`}
                    className="h-20 w-full rounded-md border p-2 font-mono text-xs"
                    value={sampleJson}
                    onChange={(e) => setSampleJson(e.target.value)}
                  />
                  <Button size="sm" onClick={() => previewMapping.mutate(m.id)}>
                    Run preview
                  </Button>
                  {previewOut && (
                    <pre className="bg-muted overflow-auto rounded-md border p-2 text-xs">
                      {previewOut}
                    </pre>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
        <div className="space-y-2 rounded-lg border p-3">
          <div className="flex flex-wrap items-end gap-2">
            <input
              aria-label="Mapping name"
              className="rounded-md border px-2 py-1 text-sm"
              placeholder="oneroster-classes"
              value={mapName}
              onChange={(e) => setMapName(e.target.value)}
            />
            <select
              aria-label="Canonical model"
              className="rounded-md border px-2 py-1 text-sm"
              value={mapModel}
              onChange={(e) => setMapModel(e.target.value)}
            >
              {[
                "roster.class",
                "roster.enrollment",
                "roster.user",
                "roster.term",
                "talent.application",
                "crm.deal",
              ].map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <Button
              size="sm"
              disabled={!mapName || createMapping.isPending}
              onClick={() => createMapping.mutate()}
            >
              Create mapping
            </Button>
          </div>
          <textarea
            aria-label="Mapping document JSON"
            className="h-32 w-full rounded-md border p-2 font-mono text-xs"
            value={mapDoc}
            onChange={(e) => setMapDoc(e.target.value)}
          />
        </div>
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
                    <li key={c.id} className="flex flex-wrap items-center gap-2 font-mono">
                      <span>
                        {c.external_id} — {c.conflict_class}
                        {Object.keys(c.detail ?? {}).length > 0 && (
                          <span className="text-muted-foreground"> {JSON.stringify(c.detail)}</span>
                        )}
                      </span>
                      {c.resolved_action ? (
                        <span className="rounded bg-green-100 px-1.5 py-0.5 text-green-800">
                          {c.resolved_action}
                        </span>
                      ) : (
                        <span className="flex gap-1">
                          {c.conflict_class === "clock_unresolvable" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                resolveConflict.mutate({ resultId: c.id, action: "accept_theirs" })
                              }
                            >
                              Accept theirs
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              resolveConflict.mutate({ resultId: c.id, action: "keep_ours" })
                            }
                          >
                            Keep ours
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              resolveConflict.mutate({ resultId: c.id, action: "dismiss" })
                            }
                          >
                            Dismiss
                          </Button>
                        </span>
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
