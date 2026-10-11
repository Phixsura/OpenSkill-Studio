"use client";

// Event mesh console (ADR-018 §12): browse canonical events, inspect
// webhook deliveries with per-attempt history, replay failed deliveries.

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface MeshEvent {
  id: string;
  type: string;
  subject: string | null;
  time: string | null;
  data: Record<string, unknown>;
}

interface Attempt {
  id: string;
  status_code: number | null;
  error: string | null;
  latency_ms: number | null;
  response_snippet: string | null;
  attempted_at: string;
}

interface Delivery {
  id: string;
  event_id: string;
  event_type: string;
  subscription_id: string;
  status: string;
  attempt_count: number;
  next_attempt_at: string | null;
  replay_of: string | null;
  attempts?: Attempt[] | null;
}

interface Subscription {
  id: string;
  url: string;
  events: string[];
  secret: string;
  active: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  succeeded: "bg-green-100 text-green-800",
  exhausted: "bg-red-100 text-red-800",
  pending: "bg-amber-100 text-amber-800",
  delivering: "bg-blue-100 text-blue-800",
  cancelled: "bg-gray-100 text-gray-800",
};

export default function IntegrationEventsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const base = `/orgs/${orgId}/integrations`;

  const [typePrefix, setTypePrefix] = useState("");
  const [subUrl, setSubUrl] = useState("");
  const [subEvents, setSubEvents] = useState("");
  const [revealedSecret, setRevealedSecret] = useState<{ id: string; secret: string } | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [openDelivery, setOpenDelivery] = useState<string | null>(null);
  const [openEvent, setOpenEvent] = useState<string | null>(null);

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ["intg-events", orgId, typePrefix],
    queryFn: () =>
      apiWithAuth<{ data: MeshEvent[] }>(
        `${base}/events${typePrefix ? `?type_prefix=${encodeURIComponent(typePrefix)}` : ""}`,
      ),
  });
  const events = eventsData?.data ?? [];

  const {
    data: deliveriesData,
    isLoading: deliveriesLoading,
    isError: deliveriesError,
  } = useQuery({
    queryKey: ["intg-deliveries", orgId, statusFilter],
    queryFn: () =>
      apiWithAuth<{ data: Delivery[] }>(
        `${base}/deliveries${statusFilter ? `?status=${statusFilter}` : ""}`,
      ),
  });
  const deliveries = deliveriesData?.data ?? [];

  const { data: detailData } = useQuery({
    queryKey: ["intg-delivery", orgId, openDelivery],
    queryFn: () => apiWithAuth<{ data: Delivery }>(`${base}/deliveries/${openDelivery}`),
    enabled: openDelivery !== null,
  });

  const catalogQ = useQuery({
    queryKey: ["intg-event-catalog", orgId],
    queryFn: () =>
      apiWithAuth<{
        data: { canonical: string[]; wildcards: string[]; internal: Record<string, string> };
      }>(`${base}/event-catalog`),
  });
  const catalogOptions = [
    ...(catalogQ.data?.data.wildcards ?? []),
    ...(catalogQ.data?.data.canonical ?? []),
    ...Object.keys(catalogQ.data?.data.internal ?? {}),
  ];

  const { data: subsData, isLoading: subsLoading } = useQuery({
    queryKey: ["intg-subs", orgId],
    queryFn: () => apiWithAuth<{ data: Subscription[] }>(`/orgs/${orgId}/webhooks`),
  });
  const subs = subsData?.data ?? [];

  const { data: subStatsData } = useQuery({
    queryKey: ["intg-sub-stats", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Record<string, Record<string, number>> }>(`${base}/subscription-stats`),
  });
  const subStats = subStatsData?.data ?? {};

  const createSub = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Subscription }>(`/orgs/${orgId}/webhooks`, {
        method: "POST",
        body: JSON.stringify({
          url: subUrl,
          events: subEvents
            .split(",")
            .map((e) => e.trim())
            .filter(Boolean),
        }),
      }),
    onSuccess: (res) => {
      setRevealedSecret({ id: res.data.id, secret: res.data.secret });
      setSubUrl("");
      setSubEvents("");
      toast.success("Subscription created — copy the signing secret now");
      queryClient.invalidateQueries({ queryKey: ["intg-subs", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Create failed"),
  });

  const rotateSub = useMutation({
    mutationFn: ({ id, immediate }: { id: string; immediate: boolean }) =>
      apiWithAuth<{ data: Subscription }>(
        `/orgs/${orgId}/webhooks/${id}/rotate-secret?immediate=${immediate}`,
        { method: "POST" },
      ),
    onSuccess: (res) => {
      setRevealedSecret({ id: res.data.id, secret: res.data.secret });
      toast.success("Secret rotated — old key co-signs 7 days unless immediate");
      queryClient.invalidateQueries({ queryKey: ["intg-subs", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Rotate failed"),
  });

  const testSub = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth<{
        data: { delivered: boolean; status_code: number | null; error: string | null };
      }>(`/orgs/${orgId}/webhooks/${id}/test`, { method: "POST" }),
    onSuccess: (res) =>
      res.data.delivered
        ? toast.success(`Test delivered (${res.data.status_code})`)
        : toast.error(`Test failed: ${res.data.error ?? res.data.status_code}`),
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Test failed"),
  });

  const toggleSub = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) =>
      apiWithAuth(`/orgs/${orgId}/webhooks/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ active }),
      }),
    onSuccess: (_d, v) => {
      toast.success(v.active ? "Subscription re-enabled" : "Subscription disabled");
      queryClient.invalidateQueries({ queryKey: ["intg-subs", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Update failed"),
  });

  const deleteSub = useMutation({
    mutationFn: (id: string) => apiWithAuth(`/orgs/${orgId}/webhooks/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Subscription deleted");
      queryClient.invalidateQueries({ queryKey: ["intg-subs", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Delete failed"),
  });

  const replay = useMutation({
    mutationFn: (id: string) => apiWithAuth(`${base}/deliveries/${id}/replay`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Replay queued");
      queryClient.invalidateQueries({ queryKey: ["intg-deliveries", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Replay failed"),
  });

  // R157: operator bulk recovery after an endpoint outage.
  const replayExhausted = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth<{ data: { requeued: number } }>(`${base}/webhooks/${id}/replay-exhausted`, {
        method: "POST",
      }),
    onSuccess: (res) => {
      toast.success(`Requeued ${res.data.requeued} exhausted deliveries`);
      queryClient.invalidateQueries({ queryKey: ["intg-deliveries", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Bulk replay failed"),
  });

  return (
    <div className="space-y-8 p-6">
      <Link
        href={`/dashboard/orgs/${orgId}/integrations`}
        className="text-muted-foreground text-sm hover:underline"
      >
        ← Integrations
      </Link>
      <div>
        <h1 className="text-2xl font-semibold">Event mesh</h1>
        <p className="text-muted-foreground text-sm">
          Canonical events with signed webhook delivery — at-least-once, retried on the Svix ladder,
          replayable after exhaustion.
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Subscriptions</h2>
        <form
          className="flex flex-wrap items-end gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            createSub.mutate();
          }}
        >
          <Input
            aria-label="Webhook URL"
            className="max-w-sm"
            placeholder="https://receiver.example.com/hooks"
            value={subUrl}
            onChange={(e) => setSubUrl(e.target.value)}
            required
          />
          <Input
            aria-label="Event patterns"
            className="max-w-sm"
            placeholder="com.openskill.integration.*, project.approved"
            list="event-catalog-options"
            value={subEvents}
            onChange={(e) => setSubEvents(e.target.value)}
            required
          />
          <datalist id="event-catalog-options">
            {catalogOptions.map((t) => (
              <option key={t} value={t} />
            ))}
          </datalist>
          <Button type="submit" size="sm" disabled={createSub.isPending}>
            Subscribe
          </Button>
        </form>
        {revealedSecret && (
          <p className="rounded-md border border-amber-300 bg-amber-50 p-2 font-mono text-xs">
            Signing secret (shown once): {revealedSecret.secret}
          </p>
        )}
        {subsLoading && <p>Loading subscriptions…</p>}
        {!subsLoading && subs.length === 0 && (
          <p className="text-muted-foreground text-sm">No subscriptions yet.</p>
        )}
        <ul className="space-y-2">
          {subs.map((sub) => (
            <li
              key={sub.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
            >
              <div className="min-w-0">
                <span className="font-mono text-xs">{sub.url}</span>
                <span className="text-muted-foreground ml-2 text-xs">{sub.events.join(", ")}</span>
                {!sub.active && <span className="ml-2 text-xs text-red-700">disabled</span>}
                {(() => {
                  const st = subStats[sub.id];
                  if (!st) return null;
                  return (
                    <span className="text-muted-foreground ml-2 text-xs">
                      {st.succeeded ?? 0} ok
                      {(st.exhausted ?? 0) > 0 && (
                        <span className="text-red-700"> / {st.exhausted} exhausted</span>
                      )}
                      {(st.pending ?? 0) > 0 && <span> / {st.pending} pending</span>}
                    </span>
                  );
                })()}
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => toggleSub.mutate({ id: sub.id, active: !sub.active })}
                >
                  {sub.active ? "Disable" : "Re-enable"}
                </Button>
                <Button size="sm" variant="outline" onClick={() => testSub.mutate(sub.id)}>
                  Test
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => rotateSub.mutate({ id: sub.id, immediate: false })}
                >
                  Rotate secret
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="text-red-700"
                  onClick={() => rotateSub.mutate({ id: sub.id, immediate: true })}
                  title="Leaked-secret path: the old key stops signing immediately"
                >
                  Rotate now
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={replayExhausted.isPending}
                  onClick={() => replayExhausted.mutate(sub.id)}
                  title="Requeue every exhausted delivery for this endpoint (after an outage)"
                >
                  Replay exhausted
                </Button>
                <Button size="sm" variant="outline" onClick={() => deleteSub.mutate(sub.id)}>
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-lg font-medium">Deliveries</h2>
          <select
            aria-label="Delivery status filter"
            className="rounded-md border px-2 py-1 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All statuses</option>
            <option value="pending">pending</option>
            <option value="succeeded">succeeded</option>
            <option value="exhausted">exhausted</option>
            <option value="cancelled">cancelled</option>
          </select>
        </div>
        {deliveriesLoading && <p>Loading deliveries…</p>}
        {deliveriesError && <p className="text-destructive">Failed to load deliveries.</p>}
        {!deliveriesLoading && deliveries.length === 0 && (
          <p className="text-muted-foreground text-sm">No deliveries yet.</p>
        )}
        <ul className="space-y-2">
          {deliveries.map((d) => (
            <li key={d.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="min-w-0">
                  <span className="font-mono text-xs">{d.event_type}</span>
                  <span
                    className={`ml-2 rounded px-2 py-0.5 text-xs ${STATUS_COLORS[d.status] ?? ""}`}
                  >
                    {d.status}
                  </span>
                  <span className="text-muted-foreground ml-2 text-xs">
                    attempts: {d.attempt_count}
                  </span>
                  {d.replay_of && <span className="ml-2 text-xs text-blue-700">replay</span>}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOpenDelivery(openDelivery === d.id ? null : d.id)}
                  >
                    Attempts
                  </Button>
                  {(d.status === "exhausted" ||
                    d.status === "cancelled" ||
                    d.status === "succeeded") && (
                    <Button size="sm" variant="outline" onClick={() => replay.mutate(d.id)}>
                      Replay
                    </Button>
                  )}
                </div>
              </div>
              {openDelivery === d.id && (
                <ul className="mt-2 space-y-1 border-t pt-2 text-xs">
                  {(detailData?.data.attempts ?? []).map((a) => (
                    <li key={a.id} className="font-mono">
                      {a.attempted_at} — {a.status_code ?? "—"}{" "}
                      {a.error && <span className="text-red-700">{a.error}</span>}
                      {a.latency_ms != null && <span> ({a.latency_ms}ms)</span>}
                      {a.response_snippet && (
                        <div className="text-muted-foreground mt-0.5 truncate">
                          ↳ {a.response_snippet}
                        </div>
                      )}
                    </li>
                  ))}
                  {detailData?.data.attempts?.length === 0 && <li>No attempts yet.</li>}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-lg font-medium">Events</h2>
          <Input
            aria-label="Type prefix filter"
            className="max-w-xs"
            placeholder="Filter by type prefix…"
            value={typePrefix}
            onChange={(e) => setTypePrefix(e.target.value)}
          />
        </div>
        {eventsLoading && <p>Loading events…</p>}
        <ul className="space-y-1">
          {events.map((e) => (
            <li key={e.id} className="rounded border px-3 py-2 text-sm">
              <button
                type="button"
                className="w-full text-left"
                onClick={() => setOpenEvent(openEvent === e.id ? null : e.id)}
              >
                <span className="font-mono text-xs">{e.type}</span>
                {e.subject && (
                  <span className="text-muted-foreground ml-2 text-xs">{e.subject}</span>
                )}
                {e.time && <span className="text-muted-foreground ml-2 text-xs">{e.time}</span>}
              </button>
              {openEvent === e.id && (
                <pre className="bg-muted mt-2 overflow-x-auto rounded p-2 text-xs">
                  {JSON.stringify(e.data, null, 2)}
                </pre>
              )}
            </li>
          ))}
          {!eventsLoading && events.length === 0 && (
            <li className="text-muted-foreground text-sm">No events recorded.</li>
          )}
        </ul>
      </section>
    </div>
  );
}
