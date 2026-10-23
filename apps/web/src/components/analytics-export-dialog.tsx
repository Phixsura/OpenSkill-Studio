"use client";

import { useState } from "react";

interface AnalyticsExportDialogProps { onExport: (format: string) => void; onClose: () => void; }

const formats = [
  { id: "json", label: "JSON", icon: "📄", description: "Machine-readable format" },
  { id: "csv", label: "CSV", icon: "📊", description: "Spreadsheet compatible" },
  { id: "markdown", label: "Markdown", icon: "📝", description: "Documentation friendly" },
];

export function AnalyticsExportDialog({ onExport, onClose }: AnalyticsExportDialogProps) {
  const [selected, setSelected] = useState("json");

  return (
    <div className="rounded-lg border bg-white p-5 shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Export Analytics</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
      </div>
      <div className="mt-4 space-y-2">
        {formats.map(f => (
          <button key={f.id} onClick={() => setSelected(f.id)}
            className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left ${selected === f.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <span className="text-xl">{f.icon}</span>
            <div>
              <p className="font-medium">{f.label}</p>
              <p className="text-xs text-gray-400">{f.description}</p>
            </div>
          </button>
        ))}
      </div>
      <button onClick={() => onExport(selected)}
        className="mt-4 w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white">
        Export as {formats.find(f => f.id === selected)?.label}
      </button>
    </div>
  );
}
