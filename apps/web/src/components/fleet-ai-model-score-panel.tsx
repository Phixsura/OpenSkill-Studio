"use client";
export function FleetAiModelScorePanel({ scorers, active, models, avgScore, dimensions }: { scorers: number; active: number; models: number; avgScore: number; dimensions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ AI Model Scoring</h3>
    <div className="text-sm">{active}/{scorers} active · {models} models · score {avgScore} · {dimensions} dimensions</div>
  </div>);
}
