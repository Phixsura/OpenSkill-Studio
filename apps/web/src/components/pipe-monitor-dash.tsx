"use client";

interface PipeRun { name: string; status: string; rowsProcessed: number; durationMs: number; }
interface PipeMonitorDashProps { runs: PipeRun[]; successRate: number; totalRows: number;
  throughput: number; healthy: boolean; }

export function PipeMonitorDash({ runs, successRate, totalRows, throughput, healthy }: PipeMonitorDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Pipeline Monitor</h3>
        <span className={`text-xs font-bold ${healthy ? "text-green-600" : "text-red-500"}`}>
          {successRate}% success · {throughput.toLocaleString()} rows/s
        </span>
      </div>
      <div className="p-3 text-xs text-gray-400 text-center">{totalRows.toLocaleString()} total rows · {runs.length} runs</div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {runs.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{r.rowsProcessed.toLocaleString()} rows</span>
              <span className={r.status === "success" ? "text-green-600" : "text-red-500"}>{r.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
