"use client";

import { useState } from "react";

interface ExportFormat { id: string; label: string; icon: string; description: string; }
interface DataExportDialogProps { formats: ExportFormat[]; rowCount: number; onExport: (formatId: string) => void; onClose: () => void; }

export function DataExportDialog({ formats, rowCount, onExport, onClose }: DataExportDialogProps) {
  const [selected, setSelected] = useState(formats[0]?.id ?? "");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full max-w-sm rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold">Export Data</h3>
        <p className="mt-1 text-sm text-gray-500">{rowCount.toLocaleString()} rows to export</p>
        <div className="mt-4 space-y-2">
          {formats.map(f => (
            <label key={f.id}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 ${selected === f.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
              <input type="radio" name="format" checked={selected === f.id} onChange={() => setSelected(f.id)} className="accent-blue-600" />
              <span className="text-lg">{f.icon}</span>
              <div>
                <p className="text-sm font-medium">{f.label}</p>
                <p className="text-xs text-gray-400">{f.description}</p>
              </div>
            </label>
          ))}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onClose} className="rounded border px-3 py-1.5 text-sm dark:border-gray-700">Cancel</button>
          <button onClick={() => onExport(selected)} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Export</button>
        </div>
      </div>
    </div>
  );
}
