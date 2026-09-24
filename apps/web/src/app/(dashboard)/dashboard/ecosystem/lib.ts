/** Shared helpers for the Ecosystem Intelligence workspace (ADR-016 Part S). */

export const SEVERITY_STYLES: Record<string, string> = {
  info: "bg-slate-100 text-slate-700",
  update_available: "bg-blue-100 text-blue-700",
  degraded: "bg-amber-100 text-amber-800",
  breaking: "bg-red-100 text-red-700",
  security_critical: "bg-red-600 text-white",
  sunset_risk: "bg-orange-100 text-orange-800",
};

export const LIFECYCLE_STYLES: Record<string, string> = {
  discovered: "bg-slate-100 text-slate-700",
  under_review: "bg-blue-100 text-blue-700",
  verified: "bg-emerald-100 text-emerald-700",
  recommended: "bg-emerald-600 text-white",
  watch: "bg-amber-100 text-amber-800",
  deprecated: "bg-orange-100 text-orange-800",
  blocked: "bg-red-100 text-red-700",
  retired: "bg-slate-300 text-slate-600",
};

export const STATUS_STYLES: Record<string, string> = {
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-amber-100 text-amber-800",
  error: "bg-red-100 text-red-700",
  archived: "bg-slate-200 text-slate-600",
  queued: "bg-slate-100 text-slate-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  pending: "bg-amber-100 text-amber-800",
  auto_merged: "bg-emerald-100 text-emerald-700",
  confirmed: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
  proposed: "bg-blue-100 text-blue-700",
  approved: "bg-emerald-100 text-emerald-700",
  draft: "bg-slate-100 text-slate-700",
  in_review: "bg-blue-100 text-blue-700",
  published: "bg-emerald-600 text-white",
  evaluating: "bg-amber-100 text-amber-800",
  promoted: "bg-emerald-600 text-white",
  aborted: "bg-slate-300 text-slate-600",
  unreviewed: "bg-amber-100 text-amber-800",
  under_review: "bg-blue-100 text-blue-700",
  superseded: "bg-slate-200 text-slate-600",
};

export function fmtDate(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  // new Date(garbage) does not throw — it yields an Invalid Date that
  // toLocaleString renders as the literal string "Invalid Date"
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

export function shortId(id: string | null | undefined): string {
  return id ? `${id.slice(0, 8)}…` : "—";
}
