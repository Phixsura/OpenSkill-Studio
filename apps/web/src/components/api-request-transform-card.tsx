"use client";

interface TransformRuleInfo {
  rule_id: string;
  action: string;
  key: string;
  value: string;
}

interface APIRequestTransformCardProps {
  rules: TransformRuleInfo[];
  appName: string;
}

const actionLabel: Record<string, string> = {
  add_header: "Add Header",
  remove_header: "Remove Header",
  add_query: "Add Query",
  rewrite_path: "Rewrite Path",
};

export default function APIRequestTransformCard({ rules, appName }: APIRequestTransformCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Request Transform</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No transform rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{actionLabel[r.action] ?? r.action}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{r.key}</span>
              </div>
              {r.value && <span className="text-gray-400">{r.value}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
