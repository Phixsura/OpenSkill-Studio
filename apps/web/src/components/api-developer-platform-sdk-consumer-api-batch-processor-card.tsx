"use client";

import { useState } from "react";

interface BatchJob {
  batchId: string;
  mode: string;
  status: string;
  requestCount: number;
  succeeded: number;
  failed: number;
}

const STATUS_COLOR: Record<string, string> = {
  completed: "text-green-600 dark:text-green-400",
  running: "text-blue-600 dark:text-blue-400",
  failed: "text-red-600 dark:text-red-400",
  pending: "text-zinc-500",
};

export default function BatchProcessorCard() {
  const [jobs] = useState<BatchJob[]>([
    { batchId: "b-001", mode: "parallel", status: "completed", requestCount: 25, succeeded: 25, failed: 0 },
    { batchId: "b-002", mode: "sequential", status: "failed", requestCount: 10, succeeded: 8, failed: 2 },
    { batchId: "b-003", mode: "parallel", status: "running", requestCount: 50, succeeded: 0, failed: 0 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Batch Processor</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Batch API request execution</p>

      <div className="mt-4 space-y-2">
        {jobs.map((j) => (
          <div key={j.batchId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{j.batchId}</span>
              <span className="ml-2 text-xs text-zinc-400">{j.mode} · {j.requestCount} reqs</span>
            </div>
            <span className={`text-xs font-medium ${STATUS_COLOR[j.status] ?? ""}`}>{j.status}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {jobs.length} batch jobs
      </div>
    </div>
  );
}
