"use client";

interface ChangeItem { id: string; title: string; risk: string; status: string; approvals: number; }
interface ChangeMgmtBoardProps { changes: ChangeItem[]; byStatus: Record<string, number>; }

const RISK_BADGE: Record<string, string> = { low: "bg-green-100 text-green-700", medium: "bg-yellow-100 text-yellow-700", high: "bg-red-100 text-red-700" };
const STATUS_STYLE: Record<string, string> = { draft: "text-gray-400", pending_review: "text-yellow-600", approved: "text-green-600", implemented: "text-blue-500" };

export function ChangeMgmtBoard({ changes, byStatus }: ChangeMgmtBoardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Change Management</h3>
        <span className="text-xs text-gray-400">{changes.length} changes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {changes.map(c => (
          <div key={c.id} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-semibold">{c.title}</span>
              <span className={`ml-2 px-1 rounded text-[10px] ${RISK_BADGE[c.risk] ?? ""}`}>{c.risk}</span>
            </div>
            <span className={`font-bold ${STATUS_STYLE[c.status] ?? ""}`}>{c.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
