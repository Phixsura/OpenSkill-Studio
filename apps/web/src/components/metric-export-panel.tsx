"use client";
interface MetricInfo { name: string; type: string; value: number; }
interface MetricExportPanelProps { metrics: MetricInfo[]; total: number; byType: Record<string, number>; }
export function MetricExportPanel({ metrics, total, byType }: MetricExportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📤 Metric Export</h3>
        <span className="text-xs text-gray-400">{total} metrics · {Object.entries(byType).map(([t,c]) => `${c} ${t}`).join(", ")}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {metrics.map(m => (
          <div key={m.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{m.name}</span>
            <div className="flex gap-2 text-gray-400">
              <span className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{m.type}</span>
              <span>{m.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
