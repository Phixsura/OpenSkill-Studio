"use client";
export function FleetComplexityPanel({ modules, avgComplexity, highComplexity, maintainable }: { modules: number; avgComplexity: number; highComplexity: number; maintainable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Complexity</h3>
    <div className={`text-lg font-bold ${maintainable ? "text-green-600" : "text-red-500"}`}>avg {avgComplexity}</div>
    <div className="text-xs text-gray-400">{modules} modules · {highComplexity} high complexity</div>
  </div>);
}
