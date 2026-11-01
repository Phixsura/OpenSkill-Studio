"use client";

interface SLAStatusInfo {
  target_id: string;
  name: string;
  metric: string;
  threshold: number;
  comparison: "gte" | "lte";
  current_value: number;
  met: boolean;
  compliance_pct: number;
  breaches: number;
  measurements: number;
}

interface SLATrackerCardProps {
  targets: SLAStatusInfo[];
  appName: string;
}

function ComplianceBar({ pct }: { pct: number }) {
  const color = pct >= 99 ? "bg-green-500" : pct >= 95 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="h-1.5 w-20 rounded-full bg-gray-200 dark:bg-gray-700">
      <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
    </div>
  );
}

export default function SLATrackerCard({ targets, appName }: SLATrackerCardProps) {
  const breachCount = targets.filter((t) => !t.met).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">SLA Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {breachCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {breachCount} breached
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All met
          </span>
        )}
      </div>

      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLA targets defined</p>
      ) : (
        <div className="space-y-3">
          {targets.map((t) => (
            <div
              key={t.target_id}
              className={`rounded-lg border px-3 py-2.5 ${
                t.met
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-red-200 dark:border-red-900/50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {t.name}
                </span>
                <span
                  className={`text-xs font-medium ${t.met ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
                >
                  {t.met ? "✓ Met" : "✕ Breached"}
                </span>
              </div>
              <div className="mt-1.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ComplianceBar pct={t.compliance_pct} />
                  <span className="text-[11px] text-gray-500">{t.compliance_pct.toFixed(1)}%</span>
                </div>
                <span className="font-mono text-xs text-gray-500">
                  {t.current_value} {t.comparison === "gte" ? "≥" : "≤"} {t.threshold}
                </span>
              </div>
              {t.breaches > 0 && (
                <p className="mt-1 text-[11px] text-red-500">
                  {t.breaches} breaches in {t.measurements} checks
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
