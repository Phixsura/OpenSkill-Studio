"use client";

interface MetricDef { name: string; type: string; value: number; help: string; }
interface MetricsExporterConfigProps { metrics: MetricDef[]; endpoint: string; scrapeIntervalSec: number; }

export function MetricsExporterConfig({ metrics, endpoint, scrapeIntervalSec }: MetricsExporterConfigProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📊 Metrics Exporter</h3>
      <div className="flex gap-4 text-xs text-gray-400 mb-4">
        <span>Endpoint: <code className="text-blue-600">{endpoint}</code></span>
        <span>Scrape: {scrapeIntervalSec}s</span>
        <span>{metrics.length} metrics</span>
      </div>
      <div className="space-y-1">
        {metrics.map(m => (
          <div key={m.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs px-1 rounded bg-blue-100 text-blue-700 dark:bg-blue-900/30">{m.type}</span>
              <span className="font-mono text-xs">{m.name}</span>
            </div>
            <span className="font-bold">{m.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
