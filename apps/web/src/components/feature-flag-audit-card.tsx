"use client";

interface AuditEntryInfo {
  entry_id: string;
  flag_key: string;
  action: string;
  actor: string;
  reason: string;
}

interface FeatureFlagAuditCardProps {
  entries: AuditEntryInfo[];
  totalCount: number;
  appName: string;
}

const actionColors: Record<string, string> = {
  created: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  enabled: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  disabled: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  deleted: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  updated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function FeatureFlagAuditCard({
  entries,
  totalCount,
  appName,
}: FeatureFlagAuditCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🏳️ Flag Audit Log
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} events</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit entries</p>
      ) : (
        <div className="space-y-1.5">
          {entries.map((e) => (
            <div
              key={e.entry_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {e.flag_key}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${actionColors[e.action] ?? ""}`}
                  >
                    {e.action}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">{e.actor}</span>
              </div>
              {e.reason && <p className="mt-0.5 text-[10px] text-gray-400">{e.reason}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
