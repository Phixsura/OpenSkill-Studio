"use client";

import { useState } from "react";

interface ExportOption { id: string; label: string; icon: string; }
interface MetricsExportDialogProps { options: ExportOption[]; onExport: (format: string) => void; onCancel: () => void; estimatedSize?: string; }

export function MetricsExportDialog({ options, onExport, onCancel, estimatedSize }: MetricsExportDialogProps) {
  const [format, setFormat] = useState(options[0]?.id || "json");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="text-lg font-semibold">Export Metrics</h2>
        <div className="mt-4 space-y-2">
          {options.map(o => (
            <label key={o.id} className="flex items-center gap-3 rounded border p-3 cursor-pointer dark:border-gray-700">
              <input type="radio" name="format" value={o.id} checked={format === o.id} onChange={() => setFormat(o.id)} />
              <span>{o.icon}</span>
              <span className="text-sm font-medium">{o.label}</span>
            </label>
          ))}
        </div>
        {estimatedSize && <p className="mt-2 text-xs text-gray-400">Estimated size: {estimatedSize}</p>}
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600">Cancel</button>
          <button onClick={() => onExport(format)} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Export</button>
        </div>
      </div>
    </div>
  );
}
