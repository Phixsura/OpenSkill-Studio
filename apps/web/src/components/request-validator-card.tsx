"use client";

interface ValidatorRuleInfo {
  rule_id: string;
  rule_type: string;
  value: string;
  enabled: boolean;
}

interface RequestValidatorCardProps {
  rules: ValidatorRuleInfo[];
  appName: string;
}

const typeLabels: Record<string, string> = {
  required_header: "Header",
  content_type: "Content-Type",
  max_size: "Max Size",
};

export default function RequestValidatorCard({ rules, appName }: RequestValidatorCardProps) {
  const enabled = rules.filter((r) => r.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ✅ Request Validator
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{rules.length} active
        </span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validation rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                  {typeLabels[r.rule_type] ?? r.rule_type}
                </span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.value}</span>
              </div>
              <span
                className={`h-2 w-2 rounded-full ${r.enabled ? "bg-green-500" : "bg-gray-400"}`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
