"use client";
export function FleetAiModelHlthV3Panel({ checkers, active, models, score, degraded, dimensions }: { checkers: number; active: number; models: number; score: number; degraded: number; dimensions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Model Health v3</h3>
    <div className="text-sm">{active}/{checkers} active · {models} models · score {score} · {degraded} degraded · {dimensions} dimensions</div>
  </div>);
}
