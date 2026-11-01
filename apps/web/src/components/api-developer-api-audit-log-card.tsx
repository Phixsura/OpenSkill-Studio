"use client";

interface EntryInfo { entry_id: string; actor: string; action: string; resource_type: string; resource_id: string; ip_address: string; }
interface Props { entries: EntryInfo[]; totalCount: number; appName: string; }

const aColor: Record<string, string> = { create: "text-green-600", update: "text-blue-600", delete: "text-red-500", access: "text-gray-500", revoke: "text-orange-600" };

export default function APIDeveloperAPIAuditLogCard({ entries, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Audit Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalCount.toLocaleString()} entries</span>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit entries</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-medium ${aColor[e.action] ?? "text-gray-500"}`}>{e.action}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.resource_type}/{e.resource_id}</span>
              </div>
              <span className="text-gray-400">{e.actor}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
