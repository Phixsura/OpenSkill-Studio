"use client";
export function FleetAiPlatBenchV3Panel({ benches, active, tests, p99, throughput }: { benches: number; active: number; tests: number; p99: number; throughput: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 AI Platform Benchmark v3</h3>
    <div className="text-sm">{active}/{benches} active · {tests} tests · p99 {p99}ms · {throughput.toLocaleString()} RPS</div>
  </div>);
}
