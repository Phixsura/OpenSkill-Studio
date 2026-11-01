"use client";
export function FleetAiPlatMaturityPanel({ assessors, active, level, dimensions, score }: { assessors: number; active: number; level: number; dimensions: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 AI Platform Maturity</h3>
    <div className="text-sm">{active}/{assessors} active · Level {level} · {dimensions} dimensions · score {score}</div>
  </div>);
}
