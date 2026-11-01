"use client";

import { useState } from "react";

interface ScoreInfo { endpoint: string; score: number; grade: string; }

const GRADE_COLOR: Record<string, string> = {
  A: "text-green-600 dark:text-green-400",
  B: "text-blue-600 dark:text-blue-400",
  C: "text-amber-600 dark:text-amber-400",
  D: "text-orange-600 dark:text-orange-400",
  F: "text-red-600 dark:text-red-400",
};

export default function HealthScoreCard() {
  const [scores] = useState<ScoreInfo[]>([
    { endpoint: "ep-auth", score: 97.5, grade: "A" },
    { endpoint: "ep-search", score: 78.2, grade: "B" },
    { endpoint: "ep-legacy", score: 45.0, grade: "D" },
  ]);

  const avg = Math.round(scores.reduce((s, e) => s + e.score, 0) / scores.length * 10) / 10;

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Health Score</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Composite health scoring per endpoint</p>

      <div className="mt-4 space-y-2">
        {scores.map((s) => (
          <div key={s.endpoint} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`text-lg font-bold ${GRADE_COLOR[s.grade]}`}>{s.grade}</span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{s.endpoint}</span>
            </div>
            <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">{s.score}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        Avg: {avg} · {scores.length} endpoints scored
      </div>
    </div>
  );
}
