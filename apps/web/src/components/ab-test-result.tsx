"use client";

interface AbTestResultProps { controlRate: number; variantRate: number; liftPct: number;
  zScore: number; significant: boolean; winner: string; confidence: string; }

export function AbTestResult({ controlRate, variantRate, liftPct, significant, winner, confidence }: AbTestResultProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 A/B Test Result</h3>
        <span className={`text-xs font-bold ${winner === "variant" ? "text-green-600" : winner === "control" ? "text-blue-500" : "text-gray-400"}`}>
          {winner} · {confidence}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Control</div><div className="font-bold text-lg">{controlRate}%</div></div>
        <div><div className="text-gray-400">Variant</div><div className="font-bold text-lg">{variantRate}%</div></div>
        <div><div className="text-gray-400">Lift</div>
          <div className={`font-bold text-lg ${liftPct > 0 ? "text-green-600" : "text-red-500"}`}>
            {liftPct > 0 ? "+" : ""}{liftPct}%
          </div>
        </div>
      </div>
      <div className="border-t dark:border-gray-700 p-3 text-center text-xs text-gray-400">
        {significant ? "✅ Statistically significant" : "⏳ Not yet significant — collect more data"}
      </div>
    </div>
  );
}
