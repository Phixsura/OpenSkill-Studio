"use client";
interface TraceSamplerPanelProps { sampled: number; total: number; actualRatePct: number; currentRate: number; }
export function TraceSamplerPanel({ sampled, total, actualRatePct, currentRate }: TraceSamplerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Adaptive Sampler</h3>
        <span className="text-xs text-gray-400">rate: {(currentRate * 100).toFixed(1)}% · {actualRatePct}% actual</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Sampled</span><div className="font-bold text-green-600 text-lg">{sampled.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">{total.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
