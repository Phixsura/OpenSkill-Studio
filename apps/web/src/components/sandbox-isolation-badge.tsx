"use client";

interface SandboxIsolationBadgeProps { isolated: boolean; issueCount: number; }

export function SandboxIsolationBadge({ isolated, issueCount }: SandboxIsolationBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
      isolated ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
               : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
    }`}>
      {isolated ? "🔒 Isolated" : `⚠️ ${issueCount} issue${issueCount !== 1 ? "s" : ""}`}
    </span>
  );
}
