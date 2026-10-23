"use client";

interface TestSuiteStatusBadgeProps { suite: string; passRate: number; status: "green" | "red"; passed: number; total: number; }

export function TestSuiteStatusBadge({ suite, passRate, status, passed, total }: TestSuiteStatusBadgeProps) {
  return (
    <div className={`inline-flex items-center gap-3 rounded-lg border px-4 py-2 ${status === "green" ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"}`}>
      <span className="text-lg">{status === "green" ? "✅" : "❌"}</span>
      <div>
        <p className="text-sm font-semibold">{suite}</p>
        <p className="text-xs text-gray-500">{passed}/{total} passed · {passRate}%</p>
      </div>
    </div>
  );
}
