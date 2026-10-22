"use client";

import { useState } from "react";

interface DataExportPanelProps { onExport: (type: string, format: string) => void; isExporting?: boolean; }

const EXPORT_TYPES = [
  { value: "full", label: "Full Export", desc: "All data including apps, analytics, reviews" },
  { value: "apps", label: "Apps Only", desc: "App definitions and configurations" },
  { value: "analytics", label: "Analytics", desc: "Usage statistics and metrics" },
];

export function DataExportPanel({ onExport, isExporting }: DataExportPanelProps) {
  const [type, setType] = useState("full");
  const [format, setFormat] = useState("json");

  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <h3 className="font-semibold">Export Data</h3>
      <p className="mt-1 text-sm text-gray-500">Download your developer platform data.</p>
      <div className="mt-4 space-y-3">
        <div>
          <label className="block text-sm font-medium">Export Type</label>
          <select value={type} onChange={e => setType(e.target.value)}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
            {EXPORT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium">Format</label>
          <div className="mt-1 flex gap-3">
            {["json", "csv"].map(f => (
              <label key={f} className="flex items-center gap-1 text-sm">
                <input type="radio" name="format" value={f} checked={format === f} onChange={() => setFormat(f)} />
                {f.toUpperCase()}
              </label>
            ))}
          </div>
        </div>
      </div>
      <button onClick={() => onExport(type, format)} disabled={isExporting}
        className="mt-4 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
        {isExporting ? "Exporting..." : "Start Export"}
      </button>
    </div>
  );
}
