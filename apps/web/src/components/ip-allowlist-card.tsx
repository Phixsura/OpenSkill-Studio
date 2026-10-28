"use client";

interface IPRuleInfo {
  rule_id: string;
  network: string;
  description: string;
}

interface IPAllowListCardProps {
  rules: IPRuleInfo[];
  mode: "allowlist" | "denylist";
  appName: string;
}

export default function IPAllowListCard({ rules, mode, appName }: IPAllowListCardProps) {
  const isAllow = mode === "allowlist";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            IP Access Control
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              isAllow
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
            }`}
          >
            {isAllow ? "Allowlist" : "Denylist"}
          </span>
          <span className="text-xs text-gray-400">{rules.length} rules</span>
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">
          {isAllow ? "No rules — all IPs allowed" : "No rules — no IPs blocked"}
        </p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span className={`text-sm ${isAllow ? "text-green-600" : "text-red-500"}`}>
                  {isAllow ? "✓" : "✕"}
                </span>
                <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                  {r.network}
                </span>
              </div>
              {r.description && <span className="text-[11px] text-gray-400">{r.description}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
