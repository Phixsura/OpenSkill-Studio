"use client";
interface ExportInfo { id: string; format: string; status: string; rowCount: number; sizeBytes: number; }
interface DataExportPanelProps { exports: ExportInfo[]; total: number; }
const FMT_BADGE: Record<string, string> = { csv: "bg-green-100 text-green-700", json: "bg-blue-100 text-blue-700", parquet: "bg-purple-100 text-purple-700" };
export function DataExportPanel({ exports, total }: DataExportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📤 Data Exports</h3>
        <span className="text-xs text-gray-400">{total} exports</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {exports.map(e => (
          <div key={e.id} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono">{e.id}</span>
              <span className={`px-1 rounded text-[10px] ${FMT_BADGE[e.format] ?? ""}`}>{e.format}</span>
            </div>
            <span className={e.status === "completed" ? "text-green-600" : e.status === "failed" ? "text-red-500" : "text-yellow-600"}>
              {e.status}{e.rowCount > 0 ? ` · ${e.rowCount.toLocaleString()} rows` : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
