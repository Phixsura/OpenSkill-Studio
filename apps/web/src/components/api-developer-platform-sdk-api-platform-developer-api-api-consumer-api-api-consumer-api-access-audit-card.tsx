"use client";

interface ReasonCount { reason: string; count: number; }
interface Props { totalEntries: number; denialRate: number; reasons: ReasonCount[]; appName: string; }

const reasonEmoji: Record<string, string> = { rate_limited: "⏱️", scope_denied: "🔒", ip_blocked: "🛡️", key_expired: "⌛", authorized: "✅" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAuditCard({ totalEntries, denialRate, reasons, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Access Audit</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalEntries.toLocaleString()} entries</p>
        </div>
        <span className={`text-sm font-bold ${denialRate < 5 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{denialRate}% denied</span>
      </div>
      {reasons.length > 0 && (
        <div className="space-y-1">
          {reasons.map((r) => (
            <div key={r.reason} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{reasonEmoji[r.reason] ?? "•"} {r.reason}</span>
              <span className="text-gray-400">{r.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
