"use client";

interface OpexScorecardProps { overall: number; level: string; doraScore: number;
  platformScore: number; doraBreakdown: Record<string, number>; }

const LEVEL_COLORS: Record<string, string> = {
  elite: "text-green-600", high: "text-blue-600", medium: "text-yellow-600", low: "text-red-600",
};

export function OpexScorecard({ overall, level, doraScore, platformScore, doraBreakdown }: OpexScorecardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${LEVEL_COLORS[level] ?? ""}`}>{overall}</div>
        <div className="text-sm text-gray-400 mt-1">Operational Excellence</div>
        <div className={`text-xs font-medium mt-1 uppercase ${LEVEL_COLORS[level] ?? ""}`}>{level}</div>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 border-b dark:border-gray-700">
        <div className="p-3 text-center">
          <div className="text-lg font-bold">{doraScore}</div>
          <div className="text-[10px] text-gray-400">DORA Score</div>
        </div>
        <div className="p-3 text-center">
          <div className="text-lg font-bold">{platformScore}</div>
          <div className="text-[10px] text-gray-400">Platform Score</div>
        </div>
      </div>
      <div className="p-3 grid grid-cols-4 gap-2">
        {Object.entries(doraBreakdown).map(([key, val]) => (
          <div key={key} className="text-center">
            <div className="text-sm font-bold">{val}</div>
            <div className="text-[9px] text-gray-400 capitalize">{key.replaceAll("_", " ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
