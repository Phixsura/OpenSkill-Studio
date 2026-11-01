"use client";
export function FleetAiIntegTestPanel({ testers, active, suites, tests, passRate }: { testers: number; active: number; suites: number; tests: number; passRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Integration Test</h3>
    <div className="text-sm">{active}/{testers} active · {suites} suites · {tests.toLocaleString()} tests · {passRate}% pass</div>
  </div>);
}
