"use client";

interface TenantIsolationBadgeProps { orgId: string; namespace: string; isolated: boolean; }

export function TenantIsolationBadge({ orgId, namespace, isolated }: TenantIsolationBadgeProps) {
  return (
    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${isolated ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"}`}>
      <span>{isolated ? "🔒" : "⚠️"}</span>
      <span>{isolated ? "Tenant Isolated" : "Isolation Warning"}</span>
      <span className="font-mono opacity-60">{namespace}</span>
    </div>
  );
}
