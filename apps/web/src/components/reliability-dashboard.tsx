"use client";

interface ReliabilityDashboardProps { reliabilityScore: number; maturity: string;
  mttrMin: number; mtbfHours: number; changeFailurePct: number; uptimePct: number; }

const MAT_COLORS: Record<string, string> = {
  advanced: "text-green-600", intermediate: "text-blue-600", basic: "text-yellow-600",
};

export function ReliabilityDashboard({ reliabilityScore, maturity, mttrMin, mtbfHours, changeFailurePct, uptimePct }: ReliabilityDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-4xl font-bold ${MAT_COLORS[maturity] ?? ""}`}>{reliabilityScore}</div>
        <div className="text-sm text-gray-400 mt-1">Reliability Score</div>
        <div className={`text-xs font-medium mt-1 capitalize ${MAT_COLORS[maturity] ?? ""}`}>{maturity}</div>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Uptime", v: `${uptimePct}%` }, { l: "MTTR", v: `${mttrMin}min` },
          { l: "MTBF", v: `${mtbfHours}h` }, { l: "CFR", v: `${changeFailurePct}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
