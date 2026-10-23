"use client";

interface Recommendation { resource: string; type: string; action: string;
  reason: string; currentCost: number; savings: number; }
interface CostOptimizerPanelProps { totalDisplay: string; savingsDisplay: string;
  savingsPct: number; recommendations: Recommendation[]; }

const ACTION_ICON: Record<string, string> = { terminate: "🗑️", downsize: "📉", reserve: "💳" };
const ACTION_COLOR: Record<string, string> = {
  terminate: "bg-red-100 text-red-700", downsize: "bg-yellow-100 text-yellow-700",
  reserve: "bg-blue-100 text-blue-700",
};

export function CostOptimizerPanel({ totalDisplay, savingsDisplay, savingsPct, recommendations }: CostOptimizerPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💡 Cost Optimizer</h3>
        <div className="text-right">
          <p className="text-sm text-gray-400">Potential savings</p>
          <p className="text-xl font-bold text-green-600">{savingsDisplay} ({savingsPct}%)</p>
        </div>
      </div>
      <p className="text-xs text-gray-400 mb-3">Current spend: {totalDisplay}</p>
      <div className="space-y-2">
        {recommendations.map(r => (
          <div key={r.resource} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span>{ACTION_ICON[r.action] || "💡"}</span>
                <span className="text-sm font-medium">{r.resource}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${ACTION_COLOR[r.action] || ""}`}>{r.action}</span>
              </div>
              <p className="text-xs text-gray-400 ml-6">{r.reason}</p>
            </div>
            <span className="text-sm font-bold text-green-600">-${r.savings.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
