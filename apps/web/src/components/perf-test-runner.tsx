"use client";

interface PerfTestResult { test: string; targetRps: number; actualRps: number;
  p99Ms: number; errorRate: number; passed: boolean; }
interface PerfTestRunnerProps { tests: PerfTestResult[]; passRate: number;
  passed: number; failed: number; }

export function PerfTestRunner({ tests, passRate, passed, failed }: PerfTestRunnerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Perf Tests</h3>
        <span className="text-xs text-gray-400">{passRate}% pass · {passed}✓ {failed}✗</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tests.map(t => (
          <div key={t.test} className="flex justify-between px-4 py-2 text-xs">
            <span className={t.passed ? "" : "text-red-600"}>{t.passed ? "✅" : "❌"} {t.test}</span>
            <span className="text-gray-400">{t.actualRps}/{t.targetRps} RPS · p99 {t.p99Ms}ms · {t.errorRate}% err</span>
          </div>
        ))}
      </div>
    </div>
  );
}
