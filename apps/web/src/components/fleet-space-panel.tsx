"use client";
export function FleetSpacePanel({ score, weakDimensions, balanced }: { score: number; weakDimensions: string[]; balanced: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌌 SPACE Framework</h3>
    <div className={`text-lg font-bold ${balanced ? "text-green-600" : "text-yellow-600"}`}>{score}/100</div>
    {weakDimensions.length > 0 && <div className="text-xs text-yellow-600">⚠️ Weak: {weakDimensions.join(", ")}</div>}
  </div>);
}
