"use client";

import { useState } from "react";

interface AnalyticsExportButtonProps { formats: string[]; rowCount: number;
  onExport: (format: string) => void; }

export function AnalyticsExportButton({ formats, rowCount, onExport }: AnalyticsExportButtonProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 rounded border px-3 py-1.5 text-xs dark:border-gray-700">
        📤 Export ({rowCount} rows)
      </button>
      {open && (
        <div className="absolute right-0 z-10 mt-1 rounded-lg border bg-white shadow-lg dark:bg-gray-900 dark:border-gray-700">
          {formats.map(f => (
            <button key={f} onClick={() => { onExport(f); setOpen(false); }}
              className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800 uppercase">{f}</button>
          ))}
        </div>
      )}
    </div>
  );
}
