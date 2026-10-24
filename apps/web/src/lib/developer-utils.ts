/**
 * Developer Platform utility functions
 */

import type { AppStatus, AppCategory, HealthScore } from "./developer-api-types";

// ── Status helpers ──────────────────────────────────

export const APP_STATUS_LABELS: Record<AppStatus, string> = {
  draft: "Draft",
  testing: "Testing",
  submitted: "In Review",
  approved: "Approved",
  published: "Published",
  deprecated: "Deprecated",
  revoked: "Revoked",
};

export const APP_STATUS_COLORS: Record<AppStatus, string> = {
  draft: "yellow",
  testing: "blue",
  submitted: "purple",
  approved: "cyan",
  published: "green",
  deprecated: "orange",
  revoked: "red",
};

export function getStatusLabel(status: string): string {
  return APP_STATUS_LABELS[status as AppStatus] ?? status;
}

export function getStatusColor(status: string): string {
  return APP_STATUS_COLORS[status as AppStatus] ?? "gray";
}

// ── Category helpers ────────────────────────────────

export const CATEGORY_ICONS: Record<AppCategory, string> = {
  connector: "🔌",
  automation: "🤖",
  analytics: "📊",
  ui_extension: "🖥️",
  ecosystem_source: "🌐",
  content_pack: "📦",
  workflow_adapter: "⚡",
};

export const CATEGORY_LABELS: Record<AppCategory, string> = {
  connector: "Connector",
  automation: "Automation",
  analytics: "Analytics",
  ui_extension: "UI Extension",
  ecosystem_source: "Ecosystem Source",
  content_pack: "Content Pack",
  workflow_adapter: "Workflow Adapter",
};

export function getCategoryIcon(category: string): string {
  return CATEGORY_ICONS[category as AppCategory] ?? "📦";
}

export function getCategoryLabel(category: string): string {
  return CATEGORY_LABELS[category as AppCategory] ?? category;
}

// ── Health helpers ───────────────────────────────────

export function getHealthStatusColor(status: HealthScore["status"]): string {
  switch (status) {
    case "healthy": return "green";
    case "degraded": return "yellow";
    case "warning": return "orange";
    case "critical": return "red";
    default: return "gray";
  }
}

export function formatErrorRate(pct: number): string {
  return `${pct.toFixed(1)}%`;
}

// ── Permission helpers ──────────────────────────────

export function groupPermissions(permissions: string[]): Record<string, string[]> {
  const groups: Record<string, string[]> = {};
  for (const perm of permissions) {
    const [action] = perm.split(":");
    if (!groups[action]) groups[action] = [];
    groups[action].push(perm);
  }
  return groups;
}

export function formatPermission(perm: string): { action: string; resource: string; icon: string } {
  const [action, resource] = perm.split(":");
  const icons: Record<string, string> = {
    read: "👁️", write: "✏️", subscribe: "🔔",
    extend: "🧩", export: "📤", run: "⚡",
  };
  return { action, resource, icon: icons[action] ?? "🔑" };
}

// ── URL helpers ─────────────────────────────────────

export function safeUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") return url;
    return null;
  } catch {
    return null;
  }
}

// ── Version helpers ─────────────────────────────────

export function compareVersions(a: string, b: string): number {
  const pa = a.split(".").map(Number);
  const pb = b.split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    const diff = (pa[i] ?? 0) - (pb[i] ?? 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

export function isNewerVersion(current: string, candidate: string): boolean {
  return compareVersions(candidate, current) > 0;
}
