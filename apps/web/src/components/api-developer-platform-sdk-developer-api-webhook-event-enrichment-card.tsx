"use client";

interface RuleInfo { rule_id: string; field_name: string; source: string; value: string; applied_count: number; }
interface Props { rules: RuleInfo[]; totalEnrichments: number; appName: string; }

const sColor: Record<string, string> = { static: "bg-gray-100 text-gray-600", consumer: "bg-blue-100 text-blue-700", timestamp: "bg-green-100 text-green-700", request_id: "bg-purple-100 text-purple-700" };

export default function APIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichmentCard({ rules, totalEnrichments, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✨ Event Enrichment</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalEnrichments.toLocaleString()} applied</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No enrichment rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${sColor[r.source] ?? ""}`}>{r.source}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.field_name}</span>
              </div>
              <span className="text-gray-400">{r.applied_count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
