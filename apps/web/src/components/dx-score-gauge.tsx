"use client";

interface DxScoreGaugeProps { score: number; grade: string; display: string; }

const GRADE_COLOR: Record<string, string> = {
  "A+": "text-green-600", A: "text-green-600", B: "text-blue-600",
  C: "text-yellow-600", D: "text-red-600",
};

export function DxScoreGauge({ score, grade, display }: DxScoreGaugeProps) {
  return (
    <div className="rounded-xl border p-6 dark:border-gray-700 text-center">
      <h3 className="font-semibold mb-3">🎯 Developer Experience</h3>
      <div className="relative w-32 h-32 mx-auto mb-3">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle cx="60" cy="60" r="50" fill="none" stroke={score >= 85 ? "#22c55e" : score >= 70 ? "#3b82f6" : score >= 50 ? "#eab308" : "#ef4444"}
            strokeWidth="10" strokeDasharray={`${score * 3.14} 314`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-black ${GRADE_COLOR[grade] || ""}`}>{grade}</span>
          <span className="text-xs text-gray-400">{score}/100</span>
        </div>
      </div>
      <p className="text-sm text-gray-500">{display}</p>
    </div>
  );
}
