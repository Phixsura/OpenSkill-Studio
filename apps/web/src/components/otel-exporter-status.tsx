"use client";

interface OtelExporterStatusProps { buffered: number; exported: number;
  batchesSent: number; batchSize: number; onFlush: () => void; }

export function OtelExporterStatus({ buffered, exported, batchesSent, batchSize, onFlush }: OtelExporterStatusProps) {
  const fillPct = Math.round((buffered / Math.max(batchSize, 1)) * 100);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📡 Trace Exporter</h3>
        <button onClick={onFlush} className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Flush</button>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{buffered}</p><p className="text-xs text-gray-400">Buffered</p></div>
        <div><p className="text-lg font-bold">{exported.toLocaleString()}</p><p className="text-xs text-gray-400">Exported</p></div>
        <div><p className="text-lg font-bold">{batchesSent}</p><p className="text-xs text-gray-400">Batches</p></div>
        <div><p className="text-lg font-bold">{batchSize}</p><p className="text-xs text-gray-400">Batch Size</p></div>
      </div>
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Buffer</span><span>{fillPct}%</span>
        </div>
        <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${fillPct > 80 ? "bg-yellow-500" : "bg-blue-500"}`}
               style={{ width: `${fillPct}%` }} />
        </div>
      </div>
    </div>
  );
}
