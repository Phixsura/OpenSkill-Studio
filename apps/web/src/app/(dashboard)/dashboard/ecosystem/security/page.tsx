"use client";
/** Security advisory registry (ADR-016 §38, Snyk/Dependabot bar). */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EcosystemNav, EmptyState, Pill } from "../components";
import { fmtDate } from "../lib";

interface Advisory {
  id: string;
  advisory_ref: string;
  title: string;
  severity: string;
  affected_kind: string | null;
  affected_ref: string;
  affected_range: string | null;
  fixed_in: string | null;
  status: string;
  created_at: string;
}

interface AffectedEntity {
  entity_kind: string;
  entity_id: string;
  canonical_name: string;
  version: string | null;
  range_match: string;
  lifecycle_status: string;
}

const SEVERITY_STYLES: Record<string, string> = {
  low: "bg-gray-100 text-gray-700",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

const STATUS_STYLES: Record<string, string> = {
  open: "bg-red-100 text-red-800",
  mitigated: "bg-emerald-100 text-emerald-800",
  dismissed: "bg-gray-100 text-gray-500",
};

const MATCH_LABEL: Record<string, string> = {
  confirmed: "in range",
  unknown_fail_open: "unknown (fail-open)",
  name_only: "name match",
};

export default function SecurityPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [form, setForm] = useState({
    advisory_ref: "",
    title: "",
    severity: "high",
    affected_ref: "",
    affected_range: "",
    fixed_in: "",
  });

  const advisories = useQuery({
    queryKey: ["eco-advisories"],
    queryFn: () => apiWithAuth<{ data: Advisory[] }>("/ecosystem/security/advisories?limit=100"),
  });
  const affected = useQuery({
    queryKey: ["eco-advisory-affected", expanded],
    enabled: Boolean(expanded),
    queryFn: () =>
      apiWithAuth<{ data: AffectedEntity[] }>(
        `/ecosystem/security/advisories/${expanded}/affected`,
      ),
  });
  const create = useMutation({
    mutationFn: () =>
      apiWithAuth("/ecosystem/security/advisories", {
        method: "POST",
        body: JSON.stringify({
          advisory_ref: form.advisory_ref,
          title: form.title,
          severity: form.severity,
          affected_ref: form.affected_ref,
          affected_range: form.affected_range || null,
          fixed_in: form.fixed_in || null,
        }),
      }),
    onSuccess: () => {
      setError(null);
      setForm({
        ...form,
        advisory_ref: "",
        title: "",
        affected_ref: "",
        affected_range: "",
        fixed_in: "",
      });
      queryClient.invalidateQueries({ queryKey: ["eco-advisories"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Registration failed"),
  });
  const transition = useMutation({
    mutationFn: ({ id, to }: { id: string; to: string }) =>
      apiWithAuth(`/ecosystem/security/advisories/${id}/status?to_status=${to}`, {
        method: "POST",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["eco-advisories"] }),
    onError: (e) => setError(e instanceof ApiError ? e.message : "Transition failed"),
  });

  const rows = advisories.data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Security Advisories</h1>
      <EcosystemNav />
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Structured advisories (CVE/GHSA/vendor). Registration emits one security change event — it
        never blocks or migrates anything by itself. Affected-entity resolution fails open: an
        unparseable version never counts as safe.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (form.advisory_ref && form.title && form.affected_ref) create.mutate();
        }}
        className="flex flex-wrap items-center gap-2 rounded-lg border bg-[hsl(var(--card))] p-3"
      >
        <input
          placeholder="CVE-2026-… / GHSA-…"
          value={form.advisory_ref}
          onChange={(e) => setForm({ ...form, advisory_ref: e.target.value })}
          className="w-44 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        />
        <input
          placeholder="title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          className="w-52 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        />
        <select
          value={form.severity}
          onChange={(e) => setForm({ ...form, severity: e.target.value })}
          className="rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        >
          {["low", "medium", "high", "critical"].map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <input
          placeholder="affected name (package/model)"
          value={form.affected_ref}
          onChange={(e) => setForm({ ...form, affected_ref: e.target.value })}
          className="w-52 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        />
        <input
          placeholder="range e.g. >=1.0 <2.4"
          value={form.affected_range}
          onChange={(e) => setForm({ ...form, affected_range: e.target.value })}
          className="w-36 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        />
        <input
          placeholder="fixed in"
          value={form.fixed_in}
          onChange={(e) => setForm({ ...form, fixed_in: e.target.value })}
          className="w-24 rounded-md border bg-[hsl(var(--background))] px-2 py-1 text-xs"
        />
        <button
          type="submit"
          className="rounded-md bg-[hsl(var(--primary))] px-3 py-1 text-xs text-[hsl(var(--primary-foreground))]"
        >
          Register advisory
        </button>
      </form>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {advisories.isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading advisories…</div>
      ) : rows.length === 0 ? (
        <EmptyState icon="🛡️" text="No advisories registered." />
      ) : (
        <div className="space-y-2">
          {rows.map((a) => (
            <div key={a.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-2">
                <Pill value={a.severity} styles={SEVERITY_STYLES} />
                <Pill value={a.status} styles={STATUS_STYLES} />
                <span className="font-mono text-xs">{a.advisory_ref}</span>
                <span className="text-sm font-medium">{a.title}</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {a.affected_ref}
                  {a.affected_range ? ` @ ${a.affected_range}` : ""}
                  {a.fixed_in ? ` → fixed in ${a.fixed_in}` : ""}
                  {" · "}
                  {fmtDate(a.created_at)}
                </span>
                <button
                  onClick={() => setExpanded(expanded === a.id ? null : a.id)}
                  className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                >
                  {expanded === a.id ? "Hide affected" : "Affected entities"}
                </button>
                {a.status === "open" && (
                  <>
                    <button
                      onClick={() => transition.mutate({ id: a.id, to: "mitigated" })}
                      className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Mark mitigated
                    </button>
                    <button
                      onClick={() => transition.mutate({ id: a.id, to: "dismissed" })}
                      className="rounded-md border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                    >
                      Dismiss
                    </button>
                  </>
                )}
              </div>
              {expanded === a.id && (
                <div className="mt-2 space-y-1 text-xs">
                  {affected.isLoading ? (
                    <span className="text-[hsl(var(--muted-foreground))]">Resolving…</span>
                  ) : (affected.data?.data ?? []).length === 0 ? (
                    <span className="text-[hsl(var(--muted-foreground))]">
                      No catalog entities match.
                    </span>
                  ) : (
                    (affected.data?.data ?? []).map((e) => (
                      <div key={e.entity_id} className="flex items-center gap-2">
                        <span className="font-medium">{e.canonical_name}</span>
                        <span className="text-[hsl(var(--muted-foreground))]">
                          ({e.entity_kind}
                          {e.version ? ` ${e.version}` : ""}) ·{" "}
                          {MATCH_LABEL[e.range_match] ?? e.range_match} · {e.lifecycle_status}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
