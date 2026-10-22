"use client";

interface SlaCheck { target: number; actual: number; met: boolean; }
interface SlaComplianceBadgeProps { compliant: boolean; checks: Record<string, SlaCheck>; }

export function SlaComplianceBadge({ compliant, checks }: SlaComplianceBadgeProps) {
  return (
    <div className={`rounded-lg border p-4 ${compliant ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"}`}>
      <div className="flex items-center gap-2">
        <span className="text-lg">{compliant ? "✅" : "⚠️"}</span>
        <h3 className="font-semibold">{compliant ? "SLA Compliant" : "SLA Violation"}</h3>
      </div>
      <ul className="mt-3 space-y-1">
        {Object.entries(checks).map(([key, check]) => (
          <li key={key} className="flex items-center justify-between text-sm">
            <span>{key.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase())}</span>
            <span className={check.met ? "text-green-600" : "text-red-600"}>
              {check.met ? "✓" : "✗"} {check.actual} / {check.target}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
