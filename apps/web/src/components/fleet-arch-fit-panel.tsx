"use client";
export function FleetArchFitPanel({ total, passing, failing, score, fit }: { total: number; passing: number; failing: number; score: number; fit: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Architecture Fitness</h3>
    <div className={`text-lg font-bold ${fit ? "text-green-600" : "text-red-500"}`}>{score}%</div>
    <div className="text-xs text-gray-400">{passing}/{total} passing · {failing} failing</div>
  </div>);
}
