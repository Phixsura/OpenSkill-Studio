"use client";
export function FleetAiSafetyBenchPanel({ benchmarks, active, tests, passRate, categories }: { benchmarks: number; active: number; tests: number; passRate: number; categories: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Safety Benchmark</h3>
    <div className="text-sm">{active}/{benchmarks} active · {tests.toLocaleString()} tests · {passRate}% pass · {categories} categories</div>
  </div>);
}
