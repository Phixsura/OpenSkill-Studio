"use client";

import { useState } from "react";

interface ReviewInfo { reviewId: string; period: string; decided: number; total: number; status: string; }

export default function AccessReviewCard() {
  const [reviews] = useState<ReviewInfo[]>([
    { reviewId: "r1", period: "2024-Q4", decided: 45, total: 45, status: "completed" },
    { reviewId: "r2", period: "2025-Q1", decided: 12, total: 38, status: "open" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Access Review</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Periodic access review with attestation</p>

      <div className="mt-4 space-y-3">
        {reviews.map((r) => (
          <div key={r.reviewId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{r.period}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${r.status === "completed" ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"}`}>{r.status}</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${(r.decided / r.total) * 100}%` }} />
            </div>
            <div className="mt-0.5 text-xs text-zinc-400">{r.decided}/{r.total} reviewed</div>
          </div>
        ))}
      </div>
    </div>
  );
}
