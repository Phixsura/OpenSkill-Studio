"use client";
/** Shared UI atoms for the Ecosystem workspace. */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";

export function Pill({ value, styles }: { value: string; styles: Record<string, string> }) {
  const cls = styles[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

const TABS = [
  { href: "/dashboard/ecosystem", label: "Overview" },
  { href: "/dashboard/ecosystem/sources", label: "Sources" },
  { href: "/dashboard/ecosystem/discoveries", label: "Discoveries" },
  { href: "/dashboard/ecosystem/catalog", label: "Catalog" },
  { href: "/dashboard/ecosystem/changes", label: "Change Feed" },
  { href: "/dashboard/ecosystem/pricing", label: "Pricing" },
  { href: "/dashboard/ecosystem/compare", label: "Compare" },
  { href: "/dashboard/ecosystem/security", label: "Security" },
  { href: "/dashboard/ecosystem/benchmarks", label: "Benchmark Lab" },
  { href: "/dashboard/ecosystem/review", label: "Blind Review" },
  { href: "/dashboard/ecosystem/components", label: "Components" },
  { href: "/dashboard/ecosystem/watchlists", label: "Watchlists" },
];

interface SearchHit {
  kind: string;
  id: string;
  canonical_name: string;
  lifecycle_status: string;
  score: number;
}

/** §15: HF-style global search — one box across all seven catalog kinds. */
export function GlobalSearch() {
  const [q, setQ] = useState("");
  const [submitted, setSubmitted] = useState("");
  const { data, isFetching } = useQuery({
    queryKey: ["eco-search", submitted],
    enabled: submitted.length > 0,
    queryFn: () =>
      apiWithAuth<{ data: SearchHit[] }>(`/ecosystem/search?q=${encodeURIComponent(submitted)}`),
  });
  const hits = submitted ? (data?.data ?? []) : [];
  return (
    <div className="relative">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(q.trim());
        }}
        className="flex gap-1"
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search catalog…"
          aria-label="Search catalog"
          className="w-48 rounded-md border bg-[hsl(var(--background))] px-2 py-1.5 text-sm"
        />
        <button type="submit" className="rounded-md border px-2 py-1.5 text-sm">
          🔍
        </button>
      </form>
      {submitted && (
        <div className="absolute z-10 mt-1 w-80 rounded-md border bg-[hsl(var(--card))] p-2 shadow-lg">
          {isFetching ? (
            <div className="p-2 text-xs text-[hsl(var(--muted-foreground))]">Searching…</div>
          ) : hits.length === 0 ? (
            <div className="p-2 text-xs text-[hsl(var(--muted-foreground))]">No matches</div>
          ) : (
            hits.map((hit) => (
              <div
                key={`${hit.kind}:${hit.id}`}
                className="flex items-center justify-between rounded px-2 py-1 text-sm hover:bg-[hsl(var(--secondary))]"
              >
                <span>
                  {hit.canonical_name}{" "}
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    ({hit.kind} · {hit.lifecycle_status})
                  </span>
                </span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {hit.score.toFixed(2)}
                </span>
              </div>
            ))
          )}
          <button
            onClick={() => setSubmitted("")}
            className="mt-1 w-full rounded border px-2 py-0.5 text-xs"
          >
            close
          </button>
        </div>
      )}
    </div>
  );
}

export function EcosystemNav() {
  const pathname = usePathname();
  return (
    <div className="flex flex-wrap items-center gap-2 border-b pb-3">
      {TABS.map((tab) => {
        const active =
          tab.href === "/dashboard/ecosystem"
            ? pathname === tab.href
            : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`rounded-md px-3 py-1.5 text-sm ${
              active
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "bg-[hsl(var(--secondary))] hover:opacity-80"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
      <div className="ml-auto">
        <GlobalSearch />
      </div>
    </div>
  );
}

export function EmptyState({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
      <div className="mb-4 text-4xl">{icon}</div>
      <p className="text-[hsl(var(--muted-foreground))]">{text}</p>
    </div>
  );
}

export function StatCard({
  label,
  value,
  alert,
  href,
}: {
  label: string;
  value: number | string;
  alert?: boolean;
  href?: string;
}) {
  const body = (
    <>
      <div className={`text-2xl font-bold ${alert ? "text-red-600" : ""}`}>{value}</div>
      <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">{label}</div>
    </>
  );
  if (href) {
    return (
      <Link
        href={href}
        className="block rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm transition hover:border-[hsl(var(--primary))]"
      >
        {body}
      </Link>
    );
  }
  return <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">{body}</div>;
}

/** mean ± CI cell from a dimension_stats entry (§15 — AA-style uncertainty). */
export function StatWithCI({
  stats,
  digits = 3,
}: {
  stats?: { mean: number; n: number; ci95: [number, number] } | null;
  digits?: number;
}) {
  if (!stats || stats.mean == null) return <span>—</span>;
  const half = (stats.ci95[1] - stats.ci95[0]) / 2;
  return (
    <span title={`n=${stats.n}, 95% CI [${stats.ci95[0]}, ${stats.ci95[1]}]`}>
      {Number(stats.mean).toFixed(digits)}
      {half > 0 && (
        <span className="text-xs text-[hsl(var(--muted-foreground))]">
          {" "}
          ±{half.toFixed(digits)}
        </span>
      )}
    </span>
  );
}
