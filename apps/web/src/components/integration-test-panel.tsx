"use client";

interface IntTest { name: string; scenario: string; outcome: "pass" | "fail" | "skip" | "error"; durationMs: number; error?: string; }
interface TestReport { total: number; passed: number; failed: number; passRate: number; durationMs: number; }

const outcomeIcons: Record<string, string> = { pass: "✅", fail: "❌", skip: "⏭", error: "💥" };

export function IntegrationTestPanel({ tests, report, onRun }: {
  tests: IntTest[]; report: TestReport; onRun?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🧪 Integration Tests</h2>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${report.passRate >= 90 ? "text-green-600" : "text-red-600"}`}>{report.passRate}%</span>
          <button onClick={onRun} className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Run Suite</button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-green-600 font-bold text-lg">{report.passed}</span>
          <span className="text-gray-500 block">passed</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-red-600 font-bold text-lg">{report.failed}</span>
          <span className="text-gray-500 block">failed</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="font-bold text-lg">{report.durationMs}ms</span>
          <span className="text-gray-500 block">duration</span>
        </div>
      </div>
      <div className="space-y-0.5">
        {tests.map((t, i) => (
          <div key={i} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{outcomeIcons[t.outcome]}</span>
              <span className="font-medium">{t.name}</span>
              <span className="text-xs text-gray-400">{t.scenario}</span>
            </div>
            <span className="text-xs text-gray-400">{t.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
