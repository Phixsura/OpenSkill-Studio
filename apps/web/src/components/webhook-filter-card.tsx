"use client";

interface FilterInfo {
  filter_id: string;
  webhook_id: string;
  patterns: string[];
  mode: "include" | "exclude";
}

interface WebhookFilterCardProps {
  filters: FilterInfo[];
  appName: string;
}

export default function WebhookFilterCard({ filters, appName }: WebhookFilterCardProps) {
  const includeCount = filters.filter((f) => f.mode === "include").length;
  const excludeCount = filters.filter((f) => f.mode === "exclude").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Webhook Filters
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {includeCount > 0 && (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              {includeCount} include
            </span>
          )}
          {excludeCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {excludeCount} exclude
            </span>
          )}
        </div>
      </div>

      {filters.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No filters — all events delivered</p>
      ) : (
        <div className="space-y-2">
          {filters.map((f) => (
            <div
              key={f.filter_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-bold ${f.mode === "include" ? "text-green-600 dark:text-green-400" : "text-red-500"}`}
                  >
                    {f.mode === "include" ? "✓" : "✕"}
                  </span>
                  <span className="text-xs text-gray-500">{f.webhook_id}</span>
                </div>
                <span
                  className={`text-[10px] font-medium uppercase ${f.mode === "include" ? "text-green-600" : "text-red-500"}`}
                >
                  {f.mode}
                </span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {f.patterns.map((p) => (
                  <span
                    key={p}
                    className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[11px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                  >
                    {p}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
