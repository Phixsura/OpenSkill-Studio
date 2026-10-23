"use client";
import { useState } from "react";

interface ExportType { type: string; description: string; supports: string[]; }
interface DataExportPageProps { types: ExportType[];
  onExport: (dataType: string, format: string) => void;
  lastExport: { dataType: string; format: string; sizeDisplay: string; recordCount: number } | null; }

export function DataExportPage({ types, onExport, lastExport }: DataExportPageProps) {
  const [selected, setSelected] = useState(types[0]?.type || "");
  const selectedType = types.find(t => t.type === selected);
  const [fmt, setFmt] = useState(selectedType?.supports[0] || "json");

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-3">📦 Data Export</h3>
      <div className="space-y-3 mb-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Data Type</label>
          <select value={selected} onChange={e => { setSelected(e.target.value); const t = types.find(x => x.type === e.target.value); if (t) setFmt(t.supports[0]); }}
            className="w-full text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600">
            {types.map(t => <option key={t.type} value={t.type}>{t.type} — {t.description}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Format</label>
          <div className="flex gap-2">
            {(selectedType?.supports || ["json"]).map(f => (
              <button key={f} onClick={() => setFmt(f)}
                className={`px-3 py-1.5 text-sm rounded uppercase ${fmt === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{f}</button>
            ))}
          </div>
        </div>
      </div>
      <button onClick={() => onExport(selected, fmt)}
        className="w-full py-2 bg-blue-600 text-white text-sm rounded font-medium hover:bg-blue-700">Export</button>
      {lastExport && (
        <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg text-sm text-green-700 dark:text-green-400">
          ✅ Exported {lastExport.recordCount} {lastExport.dataType} records ({lastExport.sizeDisplay})
        </div>
      )}
    </div>
  );
}
