"use client";

interface ExportEntry { id: string; name: string; format: string;
  rowCount: number; sizeMb: number; status: string; }
interface DataExportPanelProps { exports: ExportEntry[]; totalSizeMb: number;
  onNewExport: () => void; }

const FORMAT_COLORS: Record<string, string> = {
  csv: "bg-green-100 text-green-700", json: "bg-blue-100 text-blue-700",
  xlsx: "bg-purple-100 text-purple-700", parquet: "bg-orange-100 text-orange-700",
};

export function DataExportPanel({ exports: exportList, totalSizeMb, onNewExport }: DataExportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📤 Data Exports</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{exportList.length} exports · {totalSizeMb} MB</span>
          <button onClick={onNewExport} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Export</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {exportList.map(e => (
          <div key={e.id} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 text-[10px] rounded font-mono uppercase ${FORMAT_COLORS[e.format] ?? ""}`}>{e.format}</span>
              <span className="text-sm">{e.name}</span>
            </div>
            <div className="text-xs text-gray-400">{e.rowCount.toLocaleString()} rows · {e.sizeMb} MB</div>
          </div>
        ))}
      </div>
    </div>
  );
}
