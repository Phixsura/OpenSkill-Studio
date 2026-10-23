"use client";

import { useState } from "react";

interface Panel { key: string; title: string; icon: string; }
interface AnalyticsPageLayoutProps { appName: string; panels: Panel[]; timeRanges: string[]; exportFormats: string[];
  onTimeRangeChange: (range: string) => void; onExport: (format: string) => void; children: React.ReactNode; }

export function AnalyticsPageLayout({ appName, panels, timeRanges, exportFormats, onTimeRangeChange, onExport, children }: AnalyticsPageLayoutProps) {
  const [activeRange, setActiveRange] = useState(timeRanges[1] || "30d");
  const [activePanel, setActivePanel] = useState(panels[0]?.key || "");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{appName} Analytics</h1>
        <div className="flex gap-2">
          <div className="flex gap-1 rounded-lg border border-gray-200 p-0.5 dark:border-gray-700">
            {timeRanges.map(r => (
              <button key={r} onClick={() => { setActiveRange(r); onTimeRangeChange(r); }}
                className={`rounded px-2.5 py-1 text-xs ${activeRange === r ? "bg-blue-600 text-white" : "text-gray-500"}`}>{r}</button>
            ))}
          </div>
          <select onChange={e => onExport(e.target.value)} defaultValue=""
            className="rounded border px-2 py-1 text-xs dark:border-gray-600 dark:bg-gray-700">
            <option value="" disabled>Export</option>
            {exportFormats.map(f => <option key={f} value={f}>{f.toUpperCase()}</option>)}
          </select>
        </div>
      </div>
      <div className="flex gap-1 border-b border-gray-200 dark:border-gray-700">
        {panels.map(p => (
          <button key={p.key} onClick={() => setActivePanel(p.key)}
            className={`px-3 py-2 text-sm ${activePanel === p.key ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500"}`}>
            {p.icon} {p.title}
          </button>
        ))}
      </div>
      <div>{children}</div>
    </div>
  );
}
