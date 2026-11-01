"use client";

import { useState } from "react";

interface RuleInfo { ruleId: string; pattern: string; maskType: string; }

const MASK_COLOR: Record<string, string> = {
  full: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  partial: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  hash: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  redact: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
};

export default function DataMaskerCard() {
  const [rules] = useState<RuleInfo[]>([
    { ruleId: "r1", pattern: "password", maskType: "full" },
    { ruleId: "r2", pattern: "email", maskType: "partial" },
    { ruleId: "r3", pattern: "ssn", maskType: "hash" },
    { ruleId: "r4", pattern: "credit_card", maskType: "redact" },
  ]);
  const [totalMasked] = useState(12450);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Data Masker</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">PII/sensitive data masking engine</p>

      <div className="mt-4 space-y-2">
        {rules.map((r) => (
          <div key={r.ruleId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <code className="text-sm text-zinc-800 dark:text-zinc-200">{r.pattern}</code>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${MASK_COLOR[r.maskType] ?? ""}`}>{r.maskType}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {rules.length} rules · {totalMasked.toLocaleString()} fields masked
      </div>
    </div>
  );
}
