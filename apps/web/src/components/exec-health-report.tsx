"use client";

interface ExecHealthReportProps { score: number; grade: string; status: string;
  kpis: Record<string, string | number>; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function ExecHealthReport({ score, grade, status, kpis }: ExecHealthReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono">{score}/100</div>
        <div className="text-xs text-gray-400 capitalize">{status}</div>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        {Object.entries(kpis).map(([k, v]) => (
          <div key={k} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{v}</div>
            <div className="text-[9px] text-gray-400 capitalize">{k.replaceAll("_", " ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
