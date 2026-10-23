"use client";

interface Metric { name: string; value: number; type: string; help: string; }
interface MetricsExportPanelProps { metrics: Metric[]; prometheusContent: string;
  onCopy: () => void; onDownload: () => void; }

export function MetricsExportPanel({ metrics, prometheusContent, onCopy, onDownload }: MetricsExportPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Metrics Export</h2>
        <div className="flex gap-2">
          <button onClick={onCopy} className="rounded border px-3 py-1 text-xs dark:border-gray-600">Copy</button>
          <button onClick={onDownload} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Download</button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {metrics.map(m => (
          <div key={m.name} className="rounded border p-2 text-center dark:border-gray-700">
            <p className="text-lg font-bold">{typeof m.value === "number" && m.value < 1 ? m.value.toFixed(3) : m.value.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">{m.name.replace(/\./g, " ")}</p>
          </div>
        ))}
      </div>
      <details>
        <summary className="cursor-pointer text-xs text-gray-400">Prometheus Format</summary>
        <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-3 font-mono text-xs text-green-400">
          {prometheusContent}
        </pre>
      </details>
    </div>
  );
}
