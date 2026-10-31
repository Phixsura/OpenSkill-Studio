"use client";

import { useState } from "react";

interface ReportInfo { period: string; score: number; grade: string; recommendations: number; }

const GRADE_COLOR: Record<string, string> = {
  A: "text-green-600 dark:text-green-400",
  B: "text-blue-600 dark:text-blue-400",
  C: "text-amber-600 dark:text-amber-400",
  D: "text-orange-600 dark:text-orange-400",
  F: "text-red-600 dark:text-red-400",
};

export default function HealthReportCard() {
  const [reports] = useState<ReportInfo[]>([
    { period: "Oct 2024", score: 95, grade: "A", recommendations: 1 },
    { period: "Sep 2024", score: 78, grade: "B", recommendations: 3 },
    { period: "Aug 2024", score: 62, grade: "C", recommendations: 5 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Health Reports</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Periodic health report generation</p>

      <div className="mt-4 space-y-2">
        {reports.map((r) => (
          <div key={r.period} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`text-lg font-bold ${GRADE_COLOR[r.grade]}`}>{r.grade}</span>
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{r.period}</span>
            </div>
            <div className="text-xs text-zinc-500">
              {r.score}% · {r.recommendations} recs
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{reports.length} reports generated</div>
    </div>
  );
}
