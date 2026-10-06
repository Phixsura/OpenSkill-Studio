"use client";
/** Shared UI atoms for the Experiment Console (ADR-017 Part L). */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useQuery } from "@tanstack/react-query";
import { apiTextWithAuth, apiWithAuth } from "@/lib/api";

import { usePlatformAdmin } from "@/lib/use-me";

export function Pill({ value, styles }: { value: string; styles: Record<string, string> }) {
  const cls = styles[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

const TABS = [
  { href: "/dashboard/experiments", label: "Experiments" },
  // platformOnly tabs list/operate platform-admin endpoints — a delegated
  // org operator would only collect 403s there (defect #59)
  { href: "/dashboard/experiments/decisions", label: "Decisions", platformOnly: true },
  { href: "/dashboard/experiments/promotions", label: "Promotions", platformOnly: true },
  { href: "/dashboard/experiments/layers", label: "Layers", platformOnly: true },
  { href: "/dashboard/experiments/holdouts", label: "Holdouts", platformOnly: true },
  { href: "/dashboard/experiments/metrics", label: "Metric Explorer", platformOnly: true },
];

export function ExperimentsNav() {
  const pathname = usePathname();
  const isPlatformAdmin = usePlatformAdmin();
  return (
    <nav className="flex flex-wrap gap-2 border-b pb-2">
      {TABS.filter((tab) => !tab.platformOnly || isPlatformAdmin).map((tab) => {
        const active =
          tab.href === "/dashboard/experiments"
            ? pathname === tab.href || /^\/dashboard\/experiments\/(new|01)/i.test(pathname)
            : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              active ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">
      {message}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800"
    >
      {message}
    </div>
  );
}

export function SectionCard({
  title,
  children,
  actions,
}: {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
        {actions}
      </div>
      {children}
    </section>
  );
}

export function CsvExportButton({ path, filename }: { path: string; filename: string }) {
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  return (
    <button
      type="button"
      className="rounded-md border px-2 py-1 text-xs"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        setFailed(false);
        try {
          const text = await apiTextWithAuth(path);
          const url = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(url);
        } catch {
          // surfaced inline — an unhandled rejection here would be invisible
          setFailed(true);
        } finally {
          setBusy(false);
        }
      }}
    >
      {busy ? "Exporting…" : failed ? "Export failed — retry" : "Export CSV"}
    </button>
  );
}

/** Round 270: one-click DECISION PACKET — the record with its frozen
 * evidence as a JSON file (the audit artifact reviewers attach). */
export function JsonPacketButton({ data, filename }: { data: unknown; filename: string }) {
  return (
    <button
      type="button"
      className="rounded-md border px-2 py-1 text-xs"
      onClick={() => {
        const url = URL.createObjectURL(
          new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
        );
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
      }}
    >
      Download packet
    </button>
  );
}

/** Round 313: design-time sample-size calculator (GET /experiments/
 * planning/sample-size, round 312). Pure read — answers "how many users
 * per arm?" while the spec is being written. */
export function PlanningCalculator() {
  const [baseline, setBaseline] = useState("0.1");
  const [mde, setMde] = useState("0.1");
  const b = Number(baseline);
  const m = Number(mde);
  const valid = Number.isFinite(b) && b > 0 && b < 1 && Number.isFinite(m) && m !== 0;
  const plan = useQuery({
    queryKey: ["exp-planning", baseline, mde],
    queryFn: () =>
      apiWithAuth<{
        data: { required_n_per_arm: number | null; degenerate: boolean };
      }>(`/experiments/planning/sample-size?baseline_rate=${b}&mde_rel=${m}`),
    enabled: valid,
  });
  const n = plan.data?.data.required_n_per_arm;
  return (
    <div className="rounded-md border p-3 text-sm" data-testid="planning-calc">
      <div className="mb-2 font-medium">Sample-size planner</div>
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col text-xs">
          Baseline rate
          <input
            className="mt-1 w-24 rounded border px-2 py-1"
            value={baseline}
            onChange={(e) => setBaseline(e.target.value)}
            aria-label="baseline rate"
          />
        </label>
        <label className="flex flex-col text-xs">
          Relative MDE
          <input
            className="mt-1 w-24 rounded border px-2 py-1"
            value={mde}
            onChange={(e) => setMde(e.target.value)}
            aria-label="relative MDE"
          />
        </label>
        <div className="text-muted-foreground text-xs">
          {!valid
            ? "Enter a baseline in (0,1) and a non-zero MDE"
            : plan.data?.data.degenerate
              ? "No detectable difference at these inputs"
              : typeof n === "number"
                ? `≈ ${n.toLocaleString()} users per arm (α=0.05, power=0.8)`
                : plan.isLoading
                  ? "Computing…"
                  : ""}
        </div>
      </div>
    </div>
  );
}
