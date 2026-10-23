"use client";

interface AuditEntry { entry_id: string; actor: string; action: string; resource: string;
  timestamp: string; hash: string; }
interface AuditTrailViewerProps { entries: AuditEntry[]; chainValid: boolean; onVerify: () => void; }

export function AuditTrailViewer({ entries, chainValid, onVerify }: AuditTrailViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Audit Trail</h2>
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs ${chainValid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
            {chainValid ? "🔗 Chain Valid" : "⚠️ Chain Broken"}
          </span>
          <button onClick={onVerify} className="text-xs text-blue-500">Verify</button>
        </div>
      </div>
      <div className="space-y-1">
        {entries.map(e => (
          <div key={e.entry_id} className="flex items-center gap-2 rounded border px-3 py-2 font-mono text-xs dark:border-gray-700">
            <span className="w-16 text-gray-400">{e.timestamp.slice(11, 19)}</span>
            <span className="w-16 text-blue-500">{e.actor}</span>
            <span className="flex-1 font-bold">{e.action}</span>
            <span className="text-gray-400">{e.resource}</span>
            <span className="w-16 truncate text-[10px] text-gray-300">{e.hash.slice(0, 12)}…</span>
          </div>
        ))}
      </div>
    </div>
  );
}
