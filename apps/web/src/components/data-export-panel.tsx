"use client";
import { useState } from "react";

const resources = ["extensions", "analytics", "reviews", "users", "connectors"];
const formats = ["json", "csv", "yaml"];

export function DataExportPanel({ onExport }: { onExport?: (resource: string, format: string) => void }) {
  const [resource, setResource] = useState("extensions");
  const [format, setFormat] = useState("json");

  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-4">
      <h3 className="font-bold text-sm">Export Data</h3>
      <div>
        <label className="text-xs font-medium block mb-1">Resource</label>
        <div className="flex flex-wrap gap-1">
          {resources.map(r => (
            <button key={r} onClick={() => setResource(r)}
              className={`text-xs px-3 py-1 rounded-full capitalize ${resource === r ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{r}</button>
          ))}
        </div>
      </div>
      <div>
        <label className="text-xs font-medium block mb-1">Format</label>
        <div className="flex gap-1">
          {formats.map(f => (
            <button key={f} onClick={() => setFormat(f)}
              className={`text-xs px-3 py-1 rounded-full uppercase ${format === f ? "bg-green-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{f}</button>
          ))}
        </div>
      </div>
      <button onClick={() => onExport?.(resource, format)} className="w-full bg-blue-500 text-white rounded-lg py-2 text-sm font-medium hover:bg-blue-600">
        📥 Export {resource} as {format.toUpperCase()}
      </button>
    </div>
  );
}
