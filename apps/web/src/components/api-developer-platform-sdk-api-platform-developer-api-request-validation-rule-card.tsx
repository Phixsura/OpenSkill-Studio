"use client";

interface RuleInfo { rule_id: string; field_name: string; rule_type: string; }
interface Props { endpoint: string; rules: RuleInfo[]; totalRules: number; appName: string; }

const typeIcon: Record<string, string> = { required: "❗", regex: "🔤", min_length: "📏", max_length: "📐", enum: "📋", type: "🏷️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRuleCard({ endpoint, rules, totalRules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Validation Rules</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoint}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalRules} total rules</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validation rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{typeIcon[r.rule_type] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.field_name}</span>
              </div>
              <span className="text-gray-400">{r.rule_type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
