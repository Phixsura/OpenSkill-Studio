"use client";

import { useState } from "react";

interface CanaryReleaseSliderProps { baselineVersion: string; canaryVersion: string;
  currentPct: number; status: string; onAdvance: (pct: number) => void; onRollback: () => void; }

export function CanaryReleaseSlider({ baselineVersion, canaryVersion, currentPct, status, onAdvance, onRollback }: CanaryReleaseSliderProps) {
  const [pct, setPct] = useState(currentPct);
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Canary Release</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs ${status === "promoted" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-blue-100 text-blue-700 dark:bg-blue-900/30"}`}>
          {status}
        </span>
      </div>
      <div className="flex justify-between text-sm">
        <span>v{baselineVersion} <span className="text-gray-400">({100 - pct}%)</span></span>
        <span className="font-bold text-blue-600">v{canaryVersion} <span>({pct}%)</span></span>
      </div>
      <input type="range" min={currentPct} max={100} value={pct} onChange={e => setPct(Number(e.target.value))}
        className="w-full" disabled={status === "promoted"} />
      <div className="h-3 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
      </div>
      <div className="flex gap-2">
        <button onClick={() => onAdvance(pct)} disabled={pct === currentPct || status === "promoted"}
          className="flex-1 rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-50">
          {pct === 100 ? "Promote" : `Advance to ${pct}%`}
        </button>
        <button onClick={onRollback} disabled={status === "promoted"}
          className="rounded border border-red-300 px-4 py-2 text-sm text-red-600 disabled:opacity-50">Rollback</button>
      </div>
    </div>
  );
}
