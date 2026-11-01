"use client";
interface EpScoreInfo { endpoint: string; score: number; grade: string; }
interface EpScorePanelProps { endpoints: EpScoreInfo[]; }
const GRADE_COLOR: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function EpScorePanel({ endpoints }: EpScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💯 Endpoint Scores</h3>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{e.score}</span>
              <span className={`font-bold ${GRADE_COLOR[e.grade] ?? ""}`}>{e.grade}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
