"use client";
interface OpsScorePanelProps { score: number; grade: string; categories: Record<string, number>; service: string; }
const GRADE_COLOR: Record<string, string> = { A: "bg-green-500", B: "bg-blue-500", C: "bg-yellow-500", F: "bg-red-500" };
export function OpsScorePanel({ score, grade, categories, service }: OpsScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${GRADE_COLOR[grade] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score} — {grade}</div>
        <div className="text-xs opacity-80">{service} Operational Excellence</div>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(categories).map(([cat, val]) => (
          <div key={cat}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{cat}</span>
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
