"use client";

interface AuditEntryInfo {
  entry_id: string;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  detail: string;
}

interface AuditLogCardProps {
  entries: AuditEntryInfo[];
  totalCount: number;
  appName: string;
}

const actionStyle: Record<string, string> = {
  create: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  update: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  delete: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  access: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  login: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  logout: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

export default function AuditLogCard({ entries, totalCount, appName }: AuditLogCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Audit Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} entries</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit entries</p>
      ) : (
        <div className="space-y-1.5">
          {entries.map((e) => (
            <div
              key={e.entry_id}
              className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${actionStyle[e.action] ?? ""}`}
                  >
                    {e.action}
                  </span>
                  <span className="text-xs text-gray-700 dark:text-gray-300">
                    {e.resource_type}/{e.resource_id}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">{e.actor}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
