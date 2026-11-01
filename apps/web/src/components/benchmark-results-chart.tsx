"use client";

interface BenchResult { benchmarkId: string; name: string; meanMs: number; p95Ms: number; p99Ms: number; }

export function BenchmarkResultsChart({ results }: { results: BenchResult[] }) {
  if (!results.length) return <div className="text-center text-gray-400 py-6 text-sm">No benchmarks run</div>;
  const maxVal = Math.max(...results.map(r => r.p99Ms));

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Performance Benchmarks</h3>
      {results.map(r => (
        <div key={r.benchmarkId} className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="font-medium">{r.name}</span>
            <span className="text-gray-500">mean: {r.meanMs}ms · p95: {r.p95Ms}ms · p99: {r.p99Ms}ms</span>
          </div>
          <div className="flex gap-0.5 h-4">
            <div className="bg-green-500 rounded-l" style={{ width: `${(r.meanMs / maxVal) * 100}%` }} title={`mean: ${r.meanMs}ms`} />
            <div className="bg-yellow-500" style={{ width: `${((r.p95Ms - r.meanMs) / maxVal) * 100}%` }} title={`p95: ${r.p95Ms}ms`} />
            <div className="bg-red-400 rounded-r" style={{ width: `${((r.p99Ms - r.p95Ms) / maxVal) * 100}%` }} title={`p99: ${r.p99Ms}ms`} />
          </div>
        </div>
      ))}
      <div className="flex gap-3 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-green-500" /> Mean</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-yellow-500" /> p95</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-400" /> p99</span>
      </div>
    </div>
  );
}
