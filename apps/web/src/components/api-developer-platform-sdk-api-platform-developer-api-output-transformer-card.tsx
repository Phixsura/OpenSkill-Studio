"use client";

interface RuleInfo { rule_id: string; operation: string; field: string; applied_count: number; }
interface Props { rules: RuleInfo[]; totalTransforms: number; appName: string; }

const opIcon: Record<string, string> = { rename: "✏️", remove: "🗑️", add: "➕", format_date: "📅", mask: "🔒" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformerCard({ rules, totalTransforms, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Output Transformer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalTransforms.toLocaleString()} applied</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No transform rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{opIcon[r.operation] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.operation} → {r.field}</span>
              </div>
              <span className="text-gray-400">{r.applied_count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
