"use client";

import { useState } from "react";

interface ReportInfo {
  reportId: string;
  period: string;
  totalRequests: number;
  errorRate: number;
  status: string;
}

export default function UsageReportCard() {
  const [reports] = useState<ReportInfo[]>([
    { reportId: "r-oct", period: "Oct 2024", totalRequests: 125000, errorRate: 0.8, status: "finalized" },
    { reportId: "r-sep", period: "Sep 2024", totalRequests: 98000, errorRate: 1.2, status: "exported" },
    { reportId: "r-nov", period: "Nov 2024", totalRequests: 45000, errorRate: 0.5, status: "draft" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Usage Reports</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Periodic usage reports with export</p>

      <div className="mt-4 space-y-2">
        {reports.map((r) => (
          <div key={r.reportId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{r.period}</span>
              <span className="ml-2 text-xs text-zinc-400">{r.totalRequests.toLocaleString()} reqs</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">{r.errorRate}% err</span>
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{r.status}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{reports.length} reports</div>
    </div>
  );
}
