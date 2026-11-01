"use client";
export function FleetAiTestingV7Panel({ systems, active, tests, coverage, flaky }: { systems: number; active: number; tests: number; coverage: number; flaky: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Testing v7</h3>
    <div className="text-sm">{active}/{systems} active · {tests.toLocaleString()} tests · {coverage}% coverage · {flaky}% flaky</div>
  </div>);
}
