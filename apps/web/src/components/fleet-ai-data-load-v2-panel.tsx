"use client";
export function FleetAiDataLoadV2Panel({ loaders, active, throughput, prefetch, workers }: { loaders: number; active: number; throughput: number; prefetch: number; workers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Data Loader v2</h3>
    <div className="text-sm">{active}/{loaders} active · {throughput}Gbps · prefetch {prefetch} · {workers} workers</div>
  </div>);
}
