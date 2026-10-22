"use client";

interface CompatibilityBadgeProps { compatible: boolean; platformVersion: string; issues?: number; }

export function CompatibilityBadge({ compatible, platformVersion, issues = 0 }: CompatibilityBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
      compatible ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                 : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
    }`}>
      {compatible ? "✅" : "❌"} {compatible ? "Compatible" : `${issues} issue${issues !== 1 ? "s" : ""}`}
      <span className="text-xs opacity-60">v{platformVersion}</span>
    </span>
  );
}
