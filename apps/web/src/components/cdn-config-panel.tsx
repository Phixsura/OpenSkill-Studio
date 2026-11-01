"use client";

interface Region { id: string; name: string; }
interface CdnConfigPanelProps { regions: Region[]; cacheHitRate: number; bandwidthGb: number;
  avgLatencyMs: number; onPurge: () => void; }

export function CdnConfigPanel({ regions, cacheHitRate, bandwidthGb, avgLatencyMs, onPurge }: CdnConfigPanelProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">CDN Configuration</h2>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{cacheHitRate}%</p>
          <p className="text-xs text-gray-400">Cache Hit</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{bandwidthGb} GB</p>
          <p className="text-xs text-gray-400">Bandwidth</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{avgLatencyMs}ms</p>
          <p className="text-xs text-gray-400">Avg Latency</p>
        </div>
      </div>
      <div>
        <h3 className="text-sm font-medium">Active Regions</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {regions.map(r => (
            <span key={r.id} className="rounded-full border border-green-300 bg-green-50 px-3 py-1 text-xs dark:border-green-700 dark:bg-green-900/10">
              🌐 {r.name}
            </span>
          ))}
        </div>
      </div>
      <button onClick={onPurge} className="w-full rounded border border-red-300 py-2 text-sm text-red-600">
        Purge Cache
      </button>
    </div>
  );
}
