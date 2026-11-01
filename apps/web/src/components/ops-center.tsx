"use client";

interface OpsCenterProps { overallScore: number; status: string;
  dimensions: Record<string, number>; actionItems: string[]; }

const STATUS_BG: Record<string, string> = {
  green: "bg-green-50 dark:bg-green-900/10", yellow: "bg-yellow-50 dark:bg-yellow-900/10",
  red: "bg-red-50 dark:bg-red-900/10",
};
const STATUS_TEXT: Record<string, string> = {
  green: "text-green-600", yellow: "text-yellow-600", red: "text-red-600",
};

export function OpsCenter({ overallScore, status, dimensions, actionItems }: OpsCenterProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-6 text-center ${STATUS_BG[status] ?? ""}`}>
        <div className={`text-5xl font-bold ${STATUS_TEXT[status] ?? ""}`}>{overallScore}</div>
        <div className="text-sm text-gray-500 mt-1">Platform Operations Score</div>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {Object.entries(dimensions).map(([dim, score]) => (
          <div key={dim} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{score}%</div>
            <div className="text-[9px] text-gray-400 capitalize">{dim}</div>
          </div>
        ))}
      </div>
      {actionItems.length > 0 && (
        <div className="p-3">
          {actionItems.map((a, i) => <div key={i} className="text-xs text-red-500 py-0.5">⚠ {a}</div>)}
        </div>
      )}
    </div>
  );
}
