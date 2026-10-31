"use client";
export function FleetAiModelTestPanel({ testers, active, tests, passed, failed, passRate }: { testers: number; active: number; tests: number; passed: number; failed: number; passRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Model Testing</h3>
    <div className="text-sm">{active}/{testers} active · {tests.toLocaleString()} tests · ✅ {passed.toLocaleString()} · ❌ {failed} · {passRate}%</div>
  </div>);
}
