"use client";

interface FilterRuleInfo {
  rule_id: string;
  event_type: string;
  action: "include" | "exclude";
  field: string | null;
  operator: string;
  value: string | null;
  priority: number;
}

interface WebhookFilterCardProps {
  rules: FilterRuleInfo[];
  appName: string;
}

export default function WebhookFilterCard({ rules, appName }: WebhookFilterCardProps) {
  const includes = rules.filter((r) => r.action === "include").length;
  const excludes = rules.filter((r) => r.action === "exclude").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔽 Webhook Filters
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {includes} include · {excludes} exclude
        </span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No filter rules — all events delivered</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                      r.action === "include"
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                    }`}
                  >
                    {r.action}
                  </span>
                  <span className="text-xs text-gray-700 dark:text-gray-300">{r.event_type}</span>
                </div>
                <span className="text-[10px] text-gray-400">P{r.priority}</span>
              </div>
              {r.field && (
                <p className="mt-0.5 font-mono text-[10px] text-gray-400">
                  {r.field} {r.operator} {r.value ?? ""}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
