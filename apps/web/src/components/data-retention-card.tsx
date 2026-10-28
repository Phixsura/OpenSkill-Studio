"use client";

interface RetentionPolicyInfo {
  policy_id: string;
  data_type: string;
  retention_days: number;
  action: "delete" | "archive" | "anonymize";
  enabled: boolean;
}

interface DataRetentionCardProps {
  policies: RetentionPolicyInfo[];
  pendingPurge: number;
  appName: string;
}

const actionStyle: Record<string, string> = {
  delete: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  archive: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  anonymize: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function DataRetentionCard({
  policies,
  pendingPurge,
  appName,
}: DataRetentionCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🗑️ Data Retention
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{policies.length} policies</span>
          {pendingPurge > 0 && (
            <p className="text-[10px] text-orange-500">{pendingPurge} pending purge</p>
          )}
        </div>
      </div>

      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retention policies</p>
      ) : (
        <div className="space-y-1.5">
          {policies.map((p) => (
            <div
              key={p.policy_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!p.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {p.data_type}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${actionStyle[p.action]}`}
                >
                  {p.action}
                </span>
              </div>
              <span className="text-[11px] text-gray-400">{p.retention_days}d</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
