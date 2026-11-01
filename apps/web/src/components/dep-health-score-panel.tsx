"use client";
interface DepScore { name: string; score: number; latencyMs: number; errorRate: number; }
interface DepHealthScorePanelProps { score: number; status: string; details: DepScore[]; weakest: string; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function DepHealthScorePanel({ score, status, details, weakest }: DepHealthScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100</div>
        <div className="text-xs">{status.toUpperCase()} · weakest: {weakest}</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {details.map(d => (
          <div key={d.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{d.name}</span>
            <span className="text-gray-400">{d.score}/100 · {d.latencyMs}ms · {d.errorRate}% err</span>
          </div>
        ))}
      </div>
    </div>
  );
}
