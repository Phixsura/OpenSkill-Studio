"use client";

import Link from "next/link";
/** Watchlists + deprecation calendar (Part P). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { LIFECYCLE_STYLES, SEVERITY_STYLES, fmtDate, shortId } from "../lib";

interface Watchlist {
  id: string;
  name: string;
  org_id: string | null;
  min_severity: string;
  muted_until: string | null;
  created_at: string;
}

const SEVERITY_LEVELS = [
  "info",
  "update_available",
  "degraded",
  "sunset_risk",
  "breaking",
  "security_critical",
];
interface WatchItem {
  id: string;
  target_kind: string;
  target_id: string | null;
  target_ref: string | null;
}
interface ChangeEvent {
  id: string;
  change_type: string;
  field: string;
  severity: string;
  detected_at: string;
}
interface Sunset {
  entity_id: string;
  name: string;
  sunset_at: string;
  lifecycle_status: string;
}

export default function WatchlistsPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [orgId, setOrgId] = useState("");
  const [mutError, setMutError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [item, setItem] = useState({ target_kind: "model", target_id: "", target_ref: "" });

  // R233: the .ics / export anchors are plain browser navigations — they
  // need the narrow-scope feed token in the URL (Bearer headers don't ride)
  const feedToken = useQuery({
    queryKey: ["eco-feed-token"],
    staleTime: Infinity,
    queryFn: () => apiWithAuth<{ data: { token: string } }>("/ecosystem/export/feed-token"),
  });
  const myOrgs = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: { id: string; name: string }[] }>("/orgs"),
  });
  const watchlists = useQuery({
    queryKey: ["eco-watchlists"],
    queryFn: () => apiWithAuth<{ data: Watchlist[] }>("/ecosystem/watchlists"),
  });
  const items = useQuery({
    queryKey: ["eco-watch-items", selected],
    enabled: Boolean(selected),
    queryFn: () => apiWithAuth<{ data: WatchItem[] }>(`/ecosystem/watchlists/${selected}/items`),
  });
  const feed = useQuery({
    queryKey: ["eco-watched-changes"],
    queryFn: () => apiWithAuth<{ data: ChangeEvent[] }>("/ecosystem/watchlists/changes/feed"),
  });
  const calendar = useQuery({
    queryKey: ["eco-sunsets"],
    queryFn: () => apiWithAuth<{ data: Sunset[] }>("/ecosystem/deprecation-calendar"),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["eco-watchlists"] });
    queryClient.invalidateQueries({ queryKey: ["eco-watch-items"] });
    queryClient.invalidateQueries({ queryKey: ["eco-watched-changes"] });
  };

  // R273: self-service revocation — rotating kills every previously minted
  // feed token (leaked URL) and the anchors below re-render with the new one
  const rotateToken = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { token: string } }>("/ecosystem/export/feed-token/rotate", {
        method: "POST",
      }),
    onSuccess: (res) => {
      queryClient.setQueryData(["eco-feed-token"], { data: { token: res.data.token } });
    },
  });
  const createList = useMutation({
    mutationFn: () =>
      apiWithAuth("/ecosystem/watchlists", {
        method: "POST",
        body: JSON.stringify({ name, org_id: orgId || null }),
      }),
    onSuccess: () => {
      setName("");
      invalidate();
    },
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const updateList = useMutation({
    mutationFn: (body: {
      id: string;
      min_severity?: string;
      muted_until?: string;
      clear_mute?: boolean;
    }) =>
      apiWithAuth(`/ecosystem/watchlists/${body.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          min_severity: body.min_severity,
          muted_until: body.muted_until,
          clear_mute: body.clear_mute ?? false,
        }),
      }),
    onSuccess: () => invalidate(),
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const addItem = useMutation({
    mutationFn: () =>
      apiWithAuth(`/ecosystem/watchlists/${selected}/items`, {
        method: "POST",
        body: JSON.stringify({
          target_kind: item.target_kind,
          target_id: item.target_id || null,
          target_ref: item.target_ref || null,
        }),
      }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });
  const removeItem = useMutation({
    mutationFn: (itemId: string) =>
      apiWithAuth(`/ecosystem/watchlists/${selected}/items/${itemId}`, { method: "DELETE" }),
    onSuccess: invalidate,
    onError: (e) => setMutError(e instanceof ApiError ? e.message : "Action failed"),
  });

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Watchlists & Deprecation Calendar</h1>
      <EcosystemNav />
      {mutError && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {mutError}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">My watchlists</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (name.trim()) createList.mutate();
            }}
            className="flex gap-2"
          >
            <input
              placeholder="New watchlist name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1 rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
            />
            <select
              aria-label="Attach to organization (webhook fan-out)"
              title="Org-attached lists also fan out over the org's webhooks"
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              className="rounded-md border bg-[hsl(var(--background))] px-2 py-2 text-sm"
            >
              <option value="">personal</option>
              {(myOrgs.data?.data ?? []).map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))]"
            >
              Create
            </button>
          </form>
          {(watchlists.data?.data ?? []).map((w) => (
            <div
              key={w.id}
              className={`flex w-full items-center gap-2 rounded-lg border p-3 text-left text-sm shadow-sm ${
                selected === w.id
                  ? "border-[hsl(var(--primary))] bg-[hsl(var(--secondary))]"
                  : "bg-[hsl(var(--card))]"
              }`}
            >
              <button
                onClick={() => setSelected(selected === w.id ? null : w.id)}
                className="flex-1 text-left"
              >
                {w.name}
                {w.org_id && (
                  <span
                    title="Org-attached: changes fan out over the org's webhooks"
                    className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700"
                  >
                    org
                  </span>
                )}
                {w.muted_until && <span className="ml-2 text-xs text-amber-600">muted</span>}
              </button>
              <select
                aria-label="Notification severity threshold"
                value={w.min_severity ?? "info"}
                title="Only notify at/above this severity"
                onChange={(e) => updateList.mutate({ id: w.id, min_severity: e.target.value })}
                className="rounded-md border bg-[hsl(var(--background))] px-1 py-0.5 text-xs"
              >
                {SEVERITY_LEVELS.map((sev) => (
                  <option key={sev}>{sev}</option>
                ))}
              </select>
              <button
                aria-label={
                  w.muted_until ? "Unmute notifications" : "Mute notifications for 7 days"
                }
                title={w.muted_until ? "Unmute notifications" : "Mute notifications for 7 days"}
                onClick={() =>
                  updateList.mutate(
                    w.muted_until
                      ? { id: w.id, clear_mute: true }
                      : {
                          id: w.id,
                          muted_until: new Date(Date.now() + 7 * 86400_000).toISOString(),
                        },
                  )
                }
                className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
              >
                {w.muted_until ? "🔔" : "🔕"}
              </button>
            </div>
          ))}
          {selected && (
            <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <div className="mb-2 flex gap-2">
                <select
                  aria-label="Watch target kind"
                  value={item.target_kind}
                  onChange={(e) => setItem({ ...item, target_kind: e.target.value })}
                  className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
                >
                  {[
                    "provider",
                    "model",
                    "tool",
                    "workflow",
                    "github_repo",
                    "capability",
                    "component",
                  ].map((k) => (
                    <option key={k}>{k}</option>
                  ))}
                </select>
                <input
                  placeholder="entity id (26 chars) or leave blank"
                  value={item.target_id}
                  onChange={(e) => setItem({ ...item, target_id: e.target.value })}
                  className="flex-1 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
                />
                <input
                  placeholder="external ref (repo url…)"
                  value={item.target_ref}
                  onChange={(e) => setItem({ ...item, target_ref: e.target.value })}
                  className="flex-1 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
                />
                <button
                  onClick={() => addItem.mutate()}
                  className="rounded-md border px-2 py-1 text-xs"
                >
                  Watch
                </button>
              </div>
              {(items.data?.data ?? []).map((i) => (
                <div key={i.id} className="flex items-center justify-between py-1 text-sm">
                  <span>
                    {i.target_kind}: {i.target_ref ?? shortId(i.target_id)}
                    {i.target_id && (
                      <Link
                        href={`/dashboard/ecosystem/changes?entity=${i.target_id}`}
                        className="ml-2 text-xs text-blue-600 underline"
                      >
                        changes
                      </Link>
                    )}
                  </span>
                  <button
                    onClick={() => removeItem.mutate(i.id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Changes on watched entities</h2>
          {(feed.data?.data ?? []).length === 0 ? (
            <EmptyState icon="👀" text="No changes on your watched entities." />
          ) : (
            (feed.data?.data ?? []).map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between rounded-lg border bg-[hsl(var(--card))] p-3 text-sm shadow-sm"
              >
                <span>
                  {c.change_type} · {c.field}
                </span>
                <span className="flex items-center gap-2">
                  <Pill value={c.severity} styles={SEVERITY_STYLES} />
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {fmtDate(c.detected_at)}
                  </span>
                </span>
              </div>
            ))
          )}

          <h2 className="pt-4 text-lg font-semibold">
            Deprecation calendar (next 90 days)
            <a
              href={`/api/v1/ecosystem/deprecation-calendar.ics${
                feedToken.data?.data.token ? `?token=${feedToken.data.data.token}` : ""
              }`}
              className="ml-2 text-xs font-normal text-blue-600 underline"
            >
              📅 subscribe (.ics)
            </a>
            <button
              onClick={() => rotateToken.mutate()}
              disabled={rotateToken.isPending}
              title="Revoke every previously shared feed/calendar URL and mint a fresh token"
              className="ml-2 text-xs font-normal text-[hsl(var(--muted-foreground))] underline disabled:opacity-50"
            >
              {rotateToken.isPending
                ? "rotating…"
                : rotateToken.isSuccess
                  ? "✅ rotated — old URLs are dead"
                  : "🔄 rotate feed token"}
            </button>
            <a
              href={`/api/v1/ecosystem/export${
                feedToken.data?.data.token ? `?token=${feedToken.data.data.token}` : ""
              }`}
              className="ml-2 text-xs font-normal text-blue-600 underline"
            >
              ⬇ catalog export (JSON)
            </a>
          </h2>
          {(calendar.data?.data ?? []).length === 0 ? (
            <EmptyState icon="🗓️" text="No upcoming sunsets." />
          ) : (
            (calendar.data?.data ?? []).map((s) => (
              <div
                key={s.entity_id}
                className="flex items-center justify-between rounded-lg border border-orange-300 bg-orange-50 p-3 text-sm"
              >
                <span className="font-medium">{s.name}</span>
                <span className="flex items-center gap-2">
                  <Pill value={s.lifecycle_status} styles={LIFECYCLE_STYLES} />
                  <span className="text-xs text-orange-700">sunset {fmtDate(s.sunset_at)}</span>
                </span>
              </div>
            ))
          )}
        </section>
      </div>
    </div>
  );
}
