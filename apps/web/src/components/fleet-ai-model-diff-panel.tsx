"use client";
export function FleetAiModelDiffPanel({ differs, active, diffs, regressions, improvements }: { differs: number; active: number; diffs: number; regressions: number; improvements: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Model Diff</h3>
    <div className="text-sm">{active}/{differs} active · {diffs} diffs · {regressions} regressions · {improvements} improvements</div>
  </div>);
}
