"use client";

interface Dimension { name: string; score: number; status: string; details: string; }
interface HealthScorecardProps { overallDisplay: string; overallStatus: string;
  dimensions: Dimension[]; needsAttention: boolean; }

const STATUS_COLOR: Record<string, string> = {
  excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600",
};
const BAR_COLOR: Record<string, string> = {
  excellent: "bg-green-500", good: "bg-blue-500", fair: "bg-yellow-500", poor: "bg-red-500",
};

export function HealthScorecard({ overallDisplay, overallStatus, dimensions, needsAttention }: HealthScorecardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="text-center mb-5">
        <p className="text-4xl font-bold">{overallDisplay}</p>
        <p className={`text-sm font-medium capitalize ${STATUS_COLOR[overallStatus] || ""}`}>{overallStatus}</p>
        {needsAttention && <p className="text-xs text-red-500 mt-1">⚠️ Some dimensions need attention</p>}
      </div>
      <div className="space-y-3">
        {dimensions.map(d => (
          <div key={d.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">{d.name}</span>
              <span className={STATUS_COLOR[d.status] || ""}>{d.score}/100</span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${BAR_COLOR[d.status] || "bg-gray-400"}`}
                   style={{ width: `${d.score}%` }} />
            </div>
            {d.details && <p className="text-xs text-gray-400 mt-0.5">{d.details}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
