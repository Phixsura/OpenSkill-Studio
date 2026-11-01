"use client";

interface SecurityControl { control: string; passed: boolean; weight: number; category: string; }
interface SecPostureCardProps { score: number; grade: string; controls: SecurityControl[];
  implemented: number; total: number; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function SecPostureCard({ score, grade, controls, implemented, total }: SecPostureCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono mt-1">{score}/100</div>
        <div className="text-xs text-gray-400">Security Posture · {implemented}/{total} controls</div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {controls.map(c => (
          <div key={c.control} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span>{c.passed ? "✅" : "❌"} {c.control.replaceAll("_", " ")}</span>
            <span className="text-gray-400">{c.category} · {c.weight}pts</span>
          </div>
        ))}
      </div>
    </div>
  );
}
