"use client";

interface ValidationRuleInfo {
  key: string;
  rule_type: string;
  value: string;
}

interface APIConfigValidationCardProps {
  rules: ValidationRuleInfo[];
  errors: string[];
  appName: string;
}

export default function APIConfigValidationCard({ rules, errors, appName }: APIConfigValidationCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Config Validation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          {errors.length > 0 && <p className="text-[10px] text-red-500">{errors.length} errors</p>}
        </div>
      </div>

      {errors.length > 0 && (
        <div className="mb-3 space-y-1">
          {errors.map((e, i) => (
            <p key={i} className="text-xs text-red-600 dark:text-red-400">⚠ {e}</p>
          ))}
        </div>
      )}

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validation rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.key}</span>
              <span className="text-gray-400">{r.rule_type}{r.value ? `: ${r.value}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
