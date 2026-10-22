"use client";

interface HealthGradeCardProps { grade: string; score: number; month: string; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function HealthGradeCard({ grade, score, month }: HealthGradeCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 text-center dark:border-gray-700">
      <p className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? "text-gray-600"}`}>{grade}</p>
      <p className="text-sm text-gray-500">{score}% health · {month}</p>
    </div>
  );
}
