"use client";
interface SloInfo { name: string; current: number; target: number; }
interface SloDashPanelProps { slos: SloInfo[]; meeting: number; atRisk: number; breaching: number; overallHealth: string; }
const HEALTH_COLOR: Record<string, string> = { green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500" };
export function SloDashPanel({ slos, meeting, atRisk, breaching, overallHealth }: SloDashPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${HEALTH_COLOR[overallHealth] ?? "bg-gray-500"}`}>
        SLO Status: {meeting} meeting · {atRisk} at risk · {breaching} breaching
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slos.map(s => (
          <div key={s.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.name}</span>
            <span className={s.current >= s.target ? "text-green-600" : "text-red-500"}>
              {s.current}% / {s.target}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
