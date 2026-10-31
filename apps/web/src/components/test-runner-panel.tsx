"use client";

import { useState } from "react";

interface TestCase {
  name: string;
  result: "passed" | "failed" | "skipped" | "error";
  durationMs: number;
  errorMessage?: string;
  assertionCount: number;
}

interface TestSummary {
  suitesRun: number;
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  passRate: number;
  totalAssertions: number;
}

const resultConfig: Record<string, { color: string; icon: string }> = {
  passed: { color: "text-green-600", icon: "✅" },
  failed: { color: "text-red-600", icon: "❌" },
  skipped: { color: "text-gray-400", icon: "⏭" },
  error: { color: "text-red-800", icon: "💥" },
};

export function TestRunnerPanel({
  tests,
  summary,
  isRunning,
  onRun,
}: {
  tests: TestCase[];
  summary: TestSummary;
  isRunning: boolean;
  onRun?: () => void;
}) {
  const [filter, setFilter] = useState<string>("all");
  const filtered = filter === "all" ? tests : tests.filter((t) => t.result === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🧪 Test Runner</h2>
          {isRunning && <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />}
        </div>
        <button onClick={onRun} disabled={isRunning}
          className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg disabled:opacity-50">
          {isRunning ? "Running..." : "Run Tests"}
        </button>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Pass Rate</span>
          <span className={`font-bold text-lg ${summary.passRate >= 90 ? "text-green-600" : summary.passRate >= 70 ? "text-yellow-600" : "text-red-600"}`}>
            {summary.passRate}%
          </span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Passed</span>
          <span className="font-bold text-lg text-green-600">{summary.passed}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Failed</span>
          <span className="font-bold text-lg text-red-600">{summary.failed}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Assertions</span>
          <span className="font-bold text-lg">{summary.totalAssertions}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {["all", "passed", "failed", "skipped"].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f}
          </button>
        ))}
      </div>

      <div className="space-y-0.5">
        {filtered.map((t) => {
          const cfg = resultConfig[t.result];
          return (
            <div key={t.name} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <span className="text-sm">{t.name}</span>
                {t.assertionCount > 0 && <span className="text-xs text-gray-400">{t.assertionCount} assertions</span>}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{t.durationMs}ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
