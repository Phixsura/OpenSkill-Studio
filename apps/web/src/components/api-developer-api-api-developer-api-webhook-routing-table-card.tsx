"use client";

interface RuleInfo { rule_id: string; event_pattern: string; destination: string; enabled: boolean; matches: number; }
interface Props { rules: RuleInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiWebhookRoutingTableCard({ rules, appName }: Props) {
  const activeCount = rules.filter(r => r.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Routing Table</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{rules.length} active</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routing rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className={`flex items-center justify-between text-[11px] ${r.enabled ? "" : "opacity-40"}`}>
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-purple-50 px-1 py-0.5 text-[9px] text-purple-700 dark:bg-purple-900 dark:text-purple-200">{r.event_pattern}</span>
                <span className="text-gray-400">→</span>
                <span className="text-gray-700 dark:text-gray-300">{new URL(r.destination).hostname}</span>
              </div>
              <span className="text-gray-400">{r.matches}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
