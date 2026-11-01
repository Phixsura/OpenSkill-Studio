"use client";

interface TeamPerfCardProps { team: string; healthScore: number; rating: string;
  velocity: number; cycleTimeDays: number; deploysPerWeek: number;
  incidents: number; prReviewHours: number; }

const RATING_COLORS: Record<string, string> = {
  excellent: "text-green-600", good: "text-blue-600", needs_improvement: "text-yellow-600",
};

export function TeamPerfCard({ team, healthScore, rating, velocity, cycleTimeDays, deploysPerWeek, incidents, prReviewHours }: TeamPerfCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 {team}</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{healthScore}</span>
          <span className={`capitalize ${RATING_COLORS[rating] ?? ""}`}>{rating.replaceAll("_", " ")}</span>
        </div>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Velocity", v: velocity }, { l: "Cycle", v: `${cycleTimeDays}d` },
          { l: "Deploys/wk", v: deploysPerWeek }, { l: "Incidents", v: incidents },
          { l: "PR Review", v: `${prReviewHours}h` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
