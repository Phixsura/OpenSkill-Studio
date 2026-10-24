"use client";

interface Comparison { baseline: number; current: number; delta: number; pctChange: number; regression: boolean; }
interface PerfBaselineCardProps { comparisons: Record<string, Comparison>; hasRegression: boolean; }

export function PerfBaselineCard({ comparisons, hasRegression }: PerfBaselineCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 Performance Baseline</h3>
        <span className={`text-xs ${hasRegression ? "text-red-500" : "text-green-600"}`}>
          {hasRegression ? "⚠ Regression Detected" : "✅ Within Baseline"}
        </span>
      </div>
      <table className="w-full text-xs">
        <thead><tr className="text-gray-400 border-b dark:border-gray-700">
          <th className="p-2 text-left">Metric</th>
          <th className="p-2 text-right">Baseline</th>
          <th className="p-2 text-right">Current</th>
          <th className="p-2 text-right">Change</th>
        </tr></thead>
        <tbody>
          {Object.entries(comparisons).map(([metric, c]) => (
            <tr key={metric} className={`border-b last:border-0 dark:border-gray-700 ${c.regression ? "bg-red-50 dark:bg-red-900/5" : ""}`}>
              <td className="p-2 font-mono uppercase">{metric}</td>
              <td className="p-2 text-right">{c.baseline}ms</td>
              <td className="p-2 text-right">{c.current}ms</td>
              <td className={`p-2 text-right ${c.regression ? "text-red-500 font-bold" : ""}`}>
                {c.pctChange > 0 ? "+" : ""}{c.pctChange}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
