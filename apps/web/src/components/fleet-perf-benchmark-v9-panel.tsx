"use client";
export function FleetPerfBenchmarkV9Panel({ total, p99 }: { total: number; p99: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏎️ Perf Benchmark v9</h3>
    <div className="text-sm">{total} benchmarks · {p99}ms p99</div>
  </div>);
}
