"use client";
interface AuditEntry { userId: string; method: string; path: string; status: number; }
interface ReqAuditPanelProps { entries: AuditEntry[]; total: number; uniqueUsers: number; }
export function ReqAuditPanel({ entries, total, uniqueUsers }: ReqAuditPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Request Audit</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} logged · {uniqueUsers} users</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map((e, i) => (
          <div key={i} className="flex justify-between px-4 py-1 text-xs">
            <div className="flex gap-2">
              <span className="text-gray-400">{e.userId}</span>
              <span className="font-bold w-10">{e.method}</span>
              <span className="font-mono">{e.path}</span>
            </div>
            <span className={e.status >= 400 ? "text-red-500" : "text-green-600"}>{e.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
