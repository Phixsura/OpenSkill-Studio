"use client";
import { useState } from "react";

interface Report { reportId: string; extensionId: string; period: string; metrics: { total_events: number; by_event: Record<string, number> }; generatedAt: number; }

export function AnalyticsExportPanel({ reports, onGenerate, onExport }: {
  reports: Report[]; onGenerate?: (period: string) => void; onExport?: (reportId: string) => void;
}) {
  const [period, setPeriod] = useState("daily");
  const periods = ["daily", "weekly", "monthly"];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {periods.map(p => (
          <button key={p} onClick={() => setPeriod(p)}
            className={`text-xs px-3 py-1 rounded-full capitalize ${period === p ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{p}</button>
        ))}
        <button onClick={() => onGenerate?.(period)} className="text-xs bg-green-500 text-white px-3 py-1 rounded-lg ml-auto">Generate Report</button>
      </div>
      {reports.length === 0 ? (
        <div className="text-center text-gray-400 py-6 text-sm">No reports generated yet</div>
      ) : (
        <div className="space-y-2">
          {reports.map(r => (
            <div key={r.reportId} className="border dark:border-gray-700 rounded-xl p-3 flex items-center justify-between">
              <div>
                <span className="font-medium text-sm">{r.reportId}</span>
                <span className="text-xs text-gray-500 ml-2 capitalize">{r.period} · {r.metrics.total_events} events</span>
              </div>
              <button onClick={() => onExport?.(r.reportId)} className="text-xs bg-blue-500 text-white px-2 py-1 rounded-lg">📥 Export</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
