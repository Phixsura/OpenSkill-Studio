"use client";

interface CheckInfo { check_id: string; name: string; passed: boolean; required: boolean; }
interface Props { consumerId: string; phase: string; checks: CheckInfo[]; completionPct: number; readyForProd: boolean; appName: string; }

const phaseIcon: Record<string, string> = { not_started: "⚪", in_progress: "🔵", testing: "🟡", production: "🟢" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatusCard({ consumerId, phase, checks, completionPct, readyForProd, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Integration Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={readyForProd ? "text-sm font-bold text-green-600 dark:text-green-400" : "text-[10px] text-gray-400"}>{readyForProd ? "✅ Ready" : `${completionPct}%`}</span>
      </div>
      <div className="mb-3 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${completionPct}%` }} />
      </div>
      <div className="space-y-1">
        {checks.map((c) => (
          <div key={c.check_id} className="flex items-center gap-2 text-[11px]">
            <span>{c.passed ? "✅" : "⬜"}</span>
            <span className={c.passed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{c.name}</span>
            {!c.required && <span className="text-[9px] text-gray-400">(optional)</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
