"use client";
export function FleetAiPenTestPanel({ testers, active, tests, findings, critical }: { testers: number; active: number; tests: number; findings: number; critical: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Pen Testing</h3>
    <div className="text-sm">{active}/{testers} active · {tests} tests · {findings} findings · {critical} critical</div>
  </div>);
}
