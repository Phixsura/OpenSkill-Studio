"use client";

interface MigrationStep { table: string; rows: number; estimatedMinutes: number; strategy: string; }
interface DataMigrateCardProps { source: string; target: string; steps: MigrationStep[];
  totalRows: number; estimatedMinutes: number; }

export function DataMigrateCard({ source, target, steps, totalRows, estimatedMinutes }: DataMigrateCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Data Migration</h3>
        <span className="text-xs text-gray-400">{source} → {target} · ~{estimatedMinutes}min</span>
      </div>
      <div className="p-3 text-xs text-gray-400">{totalRows.toLocaleString()} rows across {steps.length} tables</div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {steps.map(s => (
          <div key={s.table} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.table}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{s.rows.toLocaleString()} rows</span>
              <span className={`px-1 rounded text-[10px] ${s.strategy === "bulk" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"}`}>{s.strategy}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
