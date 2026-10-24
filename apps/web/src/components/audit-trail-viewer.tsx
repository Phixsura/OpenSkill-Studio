"use client";

interface AuditEntry { seq: number; actor: string; action: string; resource: string; }
interface AuditTrailViewerProps { entries: AuditEntry[]; chainValid: boolean; total: number; }

const ACTION_STYLE: Record<string, string> = {
  create: "text-green-600", update: "text-blue-500", delete: "text-red-600",
};

export function AuditTrailViewer({ entries, chainValid, total }: AuditTrailViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Audit Trail</h3>
        <div className="flex items-center gap-2 text-xs">
          <span className={chainValid ? "text-green-600" : "text-red-500"}>
            {chainValid ? "🔗 chain valid" : "⚠ chain broken"}
          </span>
          <span className="text-gray-400">{total} entries</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.seq} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 w-6">#{e.seq}</span>
              <span className={`font-bold ${ACTION_STYLE[e.action] ?? ""}`}>{e.action}</span>
              <span className="font-mono">{e.resource}</span>
            </div>
            <span className="text-gray-400">{e.actor}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
