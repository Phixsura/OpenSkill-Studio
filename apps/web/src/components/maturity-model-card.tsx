"use client";

interface Dimension { dimension: string; score: number; max: number; description: string; }
interface MaturityModelCardProps { service: string; dimensions: Dimension[];
  level: string; maturityPct: number; totalScore: number; maxScore: number; }

const LEVEL_COLORS: Record<string, string> = {
  L5: "text-green-600", L4: "text-blue-600", L3: "text-yellow-600",
  L2: "text-orange-600", L1: "text-red-600",
};

export function MaturityModelCard({ service, dimensions, level, maturityPct, totalScore, maxScore }: MaturityModelCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Maturity: {service}</h3>
        <div className="flex gap-2">
          <span className={`text-sm font-bold ${LEVEL_COLORS[level] ?? ""}`}>{level}</span>
          <span className="text-xs text-gray-400">{totalScore}/{maxScore} ({maturityPct}%)</span>
        </div>
      </div>
      <div className="p-3 space-y-2">
        {dimensions.map(d => (
          <div key={d.dimension}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{d.dimension}</span>
              <span className="font-mono">{d.score}/{d.max}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${d.score >= 4 ? "bg-green-500" : d.score >= 3 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${(d.score / d.max) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
