"use client";
import { useState } from "react";

interface AnalyticsExportBtnProps { formats: string[]; period: string;
  onExport: (fmt: string) => void; lastExport: { format: string; sizeDisplay: string } | null; }

export function AnalyticsExportBtn({ formats, period, onExport, lastExport }: AnalyticsExportBtnProps) {
  const [fmt, setFmt] = useState(formats[0] || "json");
  return (
    <div className="flex items-center gap-2">
      <select value={fmt} onChange={e => setFmt(e.target.value)}
        className="text-xs px-2 py-1 border rounded dark:bg-gray-800 dark:border-gray-600 uppercase">
        {formats.map(f => <option key={f} value={f}>{f}</option>)}
      </select>
      <button onClick={() => onExport(fmt)}
        className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
        📥 Export {period}
      </button>
      {lastExport && <span className="text-xs text-gray-400">Last: {lastExport.sizeDisplay}</span>}
    </div>
  );
}
