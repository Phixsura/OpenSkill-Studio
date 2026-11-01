"use client";

interface EndpointProfile { endpoint: string; method: string; p50_ms: number; p95_ms: number; p99_ms: number; is_slow: boolean; score: number; }
interface PerformanceProfilerViewProps { endpoints: EndpointProfile[]; overallScore: number; avgP95Ms: number; slowCount: number; }

export function PerformanceProfilerView({ endpoints, overallScore, avgP95Ms, slowCount }: PerformanceProfilerViewProps) {
  const scoreColor = overallScore >= 80 ? "text-green-600" : overallScore >= 50 ? "text-yellow-600" : "text-red-600";
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Performance Profile</h2>
        <span className={`text-2xl font-bold ${scoreColor}`}>{overallScore}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
          <p className="font-bold">{avgP95Ms}ms</p><p className="text-xs text-gray-400">Avg P95</p>
        </div>
        <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
          <p className={`font-bold ${slowCount > 0 ? "text-red-600" : "text-green-600"}`}>{slowCount}</p>
          <p className="text-xs text-gray-400">Slow Endpoints</p>
        </div>
      </div>
      <div className="space-y-1.5">
        {endpoints.map(ep => (
          <div key={`${ep.method}-${ep.endpoint}`} className={`rounded-lg border p-3 dark:border-gray-700 ${ep.is_slow ? "border-red-200 dark:border-red-800" : ""}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">{ep.method}</span>
                <span className="font-mono text-sm">{ep.endpoint}</span>
                {ep.is_slow && <span className="text-xs text-red-500">⚠ Slow</span>}
              </div>
              <span className="text-xs text-gray-400">Score: {ep.score}</span>
            </div>
            <div className="mt-1 flex gap-4 text-xs text-gray-400">
              <span>P50: {ep.p50_ms}ms</span>
              <span>P95: {ep.p95_ms}ms</span>
              <span>P99: {ep.p99_ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
