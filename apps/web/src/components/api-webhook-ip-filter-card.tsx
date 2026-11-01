"use client";

interface IPFilterInfo {
  rule_id: string;
  cidr: string;
  action: "allow" | "block";
}

interface APIWebhookIPFilterCardProps {
  rules: IPFilterInfo[];
  blockedCount: number;
  appName: string;
}

export default function APIWebhookIPFilterCard({ rules, blockedCount, appName }: APIWebhookIPFilterCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚫 Webhook IP Filter</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          {blockedCount > 0 && <p className="text-[10px] text-red-500">{blockedCount} blocked</p>}
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP filter rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.cidr}</span>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${r.action === "block" ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300" : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"}`}>{r.action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
