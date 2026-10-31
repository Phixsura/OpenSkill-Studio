"use client";

interface AlertRuleInfo {
  rule_id: string;
  name: string;
  metric: string;
  operator: "gt" | "lt" | "gte" | "lte" | "eq";
  threshold: number;
  state: "ok" | "firing" | "resolved";
  enabled: boolean;
}

interface AlertRulesCardProps {
  rules: AlertRuleInfo[];
  appName: string;
}

const OP_SYMBOLS: Record<string, string> = { gt: ">", lt: "<", gte: "≥", lte: "≤", eq: "=" };
const STATE_STYLES: Record<string, { dot: string; label: string }> = {
  ok: { dot: "bg-green-500", label: "OK" },
  firing: { dot: "bg-red-500 animate-pulse", label: "Firing" },
  resolved: { dot: "bg-blue-500", label: "Resolved" },
};

export default function AlertRulesCard({ rules, appName }: AlertRulesCardProps) {
  const firingCount = rules.filter((r) => r.state === "firing").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Alert Rules</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {firingCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {firingCount} firing
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All clear
          </span>
        )}
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alert rules</p>
      ) : (
        <div className="space-y-2">
          {rules.map((r) => {
            const st = STATE_STYLES[r.state] ?? STATE_STYLES.ok;
            return (
              <div
                key={r.rule_id}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 ${
                  r.state === "firing"
                    ? "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/20"
                    : "border-gray-100 dark:border-gray-800"
                } ${!r.enabled ? "opacity-50" : ""}`}
              >
                <div className="flex items-center gap-2.5">
                  <span className={`h-2.5 w-2.5 rounded-full ${st.dot}`} />
                  <div>
                    <span className="text-sm text-gray-800 dark:text-gray-200">{r.name}</span>
                    <p className="font-mono text-[11px] text-gray-400">
                      {r.metric} {OP_SYMBOLS[r.operator] ?? r.operator} {r.threshold}
                    </p>
                  </div>
                </div>
                <span
                  className={`text-xs font-medium ${r.state === "firing" ? "text-red-600 dark:text-red-400" : "text-gray-500"}`}
                >
                  {st.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
