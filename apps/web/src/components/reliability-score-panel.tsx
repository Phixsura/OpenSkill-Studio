"use client";
interface ReliabilityScorePanelProps { service: string; score: number; grade: string;
  breakdown: Record<string, number>; }
const GRADE_COLOR: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function ReliabilityScorePanel({ service, score, grade, breakdown }: ReliabilityScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏆 Reliability: {service}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xl font-black">{score}</span>
          <span className={`text-xl font-black ${GRADE_COLOR[grade] ?? ""}`}>{grade}</span>
        </div>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(breakdown).map(([dim, val]) => (
          <div key={dim}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{dim.replace("_", " ")}</span>
              <span className="text-gray-400">{val}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${val >= 80 ? "bg-green-500" : val >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${val}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
