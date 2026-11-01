"use client";

import { useState } from "react";

interface ComplianceInfo {
  framework: string;
  score: number;
  passed: number;
  total: number;
}

export default function ComplianceCheckerCard() {
  const [frameworks] = useState<ComplianceInfo[]>([
    { framework: "GDPR", score: 100, passed: 8, total: 8 },
    { framework: "SOC2", score: 87.5, passed: 7, total: 8 },
    { framework: "PCI DSS", score: 66.7, passed: 4, total: 6 },
  ]);

  const getColor = (score: number) => {
    if (score >= 100) return "text-green-600 dark:text-green-400";
    if (score >= 80) return "text-amber-600 dark:text-amber-400";
    return "text-red-600 dark:text-red-400";
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Compliance Checker</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Regulatory compliance validation</p>

      <div className="mt-4 space-y-2">
        {frameworks.map((f) => (
          <div key={f.framework} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{f.framework}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400">{f.passed}/{f.total} rules</span>
              <span className={`text-sm font-bold ${getColor(f.score)}`}>{f.score}%</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {frameworks.filter((f) => f.score === 100).length}/{frameworks.length} frameworks fully compliant
      </div>
    </div>
  );
}
