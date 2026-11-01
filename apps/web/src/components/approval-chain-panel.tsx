"use client";
interface Level { approver: string; role: string; approved: boolean; }
interface ApprovalChainPanelProps { deployId: string; status: string; levels: Level[]; currentLevel: number; }
export function ApprovalChainPanel({ deployId, status, levels, currentLevel }: ApprovalChainPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Approval Chain: {deployId}</h3>
        <span className={`text-xs font-bold ${status === "fully_approved" ? "text-green-600" : "text-yellow-600"}`}>
          {status === "fully_approved" ? "✅ Approved" : `⏳ Level ${currentLevel + 1}/${levels.length}`}
        </span>
      </div>
      <div className="p-4 space-y-1">
        {levels.map((l, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span>{l.approved ? "✅" : (i === currentLevel ? "⏳" : "⬜")}</span>
            <span className={l.approved ? "" : "text-gray-400"}>{l.approver} ({l.role})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
