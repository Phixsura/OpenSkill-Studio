"use client";
interface EpBenchmarkPanelProps { endpoint: string; samples: number; avgMs: number;
  p50Ms: number; p95Ms: number; p99Ms: number; throughputRps: number; verdict: string; }
export function EpBenchmarkPanel({ endpoint, samples, avgMs, p50Ms, p95Ms, p99Ms, throughputRps, verdict }: EpBenchmarkPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏎️ Benchmark: {endpoint}</h3>
        <span className={`text-xs font-bold ${verdict === "ok" ? "text-green-600" : "text-red-500"}`}>
          {verdict} · {throughputRps} rps · {samples} samples
        </span>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Avg</span><div className="font-bold">{avgMs}ms</div></div>
        <div><span className="text-gray-400">P50</span><div className="font-bold">{p50Ms}ms</div></div>
        <div><span className="text-gray-400">P95</span><div className="font-bold">{p95Ms}ms</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
      </div>
    </div>
  );
}
