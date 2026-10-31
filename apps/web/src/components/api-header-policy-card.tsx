"use client";

interface HeaderRuleInfo {
  rule_id: string;
  header_name: string;
  action: "require" | "forbid" | "set_default";
  value: string;
}

interface APIHeaderPolicyCardProps {
  rules: HeaderRuleInfo[];
  appName: string;
}

const actionStyle: Record<string, string> = {
  require: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  forbid: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  set_default: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
};

export default function APIHeaderPolicyCard({ rules, appName }: APIHeaderPolicyCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Header Policy</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No header rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${actionStyle[r.action]}`}>{r.action.replace("_", " ")}</span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{r.header_name}</span>
              </div>
              {r.value && <span className="text-[10px] text-gray-400">{r.value}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
