"use client";
interface AuditEntry { key: string; changedBy: string; env: string; oldHash: string; newHash: string; }
interface ConfigAuditPanelProps { entries: AuditEntry[]; totalChanges: number; }
export function ConfigAuditPanel({ entries, totalChanges }: ConfigAuditPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Config Audit</h3>
        <span className="text-xs text-gray-400">{totalChanges} changes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map((e, i) => (
          <div key={i} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono">{e.key}</span>
              <span className="text-gray-400">{e.changedBy} · {e.env}</span>
            </div>
            <span className="text-gray-400 font-mono text-[10px]">{e.oldHash} → {e.newHash}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
