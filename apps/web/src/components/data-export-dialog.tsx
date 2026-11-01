"use client";
import { useState } from "react";

interface DataExportDialogProps {
  availableFormats: string[];
  rowCount: number;
  onExport: (format: string) => void;
}

export function DataExportDialog({ availableFormats, rowCount, onExport }: DataExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState(availableFormats[0] || "csv");
  const [exporting, setExporting] = useState(false);

  const handleExport = () => {
    setExporting(true);
    onExport(selectedFormat);
    setTimeout(() => setExporting(false), 1000);
  };

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-md">
      <h3 className="font-semibold mb-3">📥 Export Data</h3>
      <p className="text-sm text-gray-500 mb-4">{rowCount.toLocaleString()} rows available</p>
      <div className="mb-4">
        <label className="block text-xs text-gray-400 mb-1">Format</label>
        <div className="flex gap-2">
          {availableFormats.map(f => (
            <button key={f} onClick={() => setSelectedFormat(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium uppercase transition ${
                selectedFormat === f
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
              }`}>{f}</button>
          ))}
        </div>
      </div>
      <button onClick={handleExport} disabled={exporting}
        className="w-full py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
        {exporting ? "Exporting..." : `Export as ${selectedFormat.toUpperCase()}`}
      </button>
    </div>
  );
}
