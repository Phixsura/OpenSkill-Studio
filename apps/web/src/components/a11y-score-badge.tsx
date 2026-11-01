"use client";

interface A11yCheck { id: string; label: string; category: string; passed: boolean; }
interface A11yScoreBadgeProps { score: number; grade: string; checks: A11yCheck[];
  passed: number; total: number; }

const gradeColor: Record<string, string> = {
  A: "from-green-500 to-emerald-600", B: "from-blue-500 to-cyan-600",
  C: "from-yellow-500 to-orange-500", F: "from-red-500 to-pink-600",
};
const catIcon: Record<string, string> = {
  perceivable: "👁️", operable: "⌨️", understandable: "🧠", robust: "🔧",
};

export function A11yScoreBadge({ score, grade, checks, passed, total }: A11yScoreBadgeProps) {
  return (
    <div className="space-y-4">
      <div className={`rounded-xl bg-gradient-to-r ${gradeColor[grade] ?? gradeColor.C} p-6 text-center text-white`}>
        <p className="text-5xl font-black">{grade}</p>
        <p className="mt-1 text-2xl font-bold">{score}/100</p>
        <p className="text-sm opacity-80">Accessibility Score · {passed}/{total} checks</p>
      </div>
      <div className="space-y-1.5">
        {checks.map(c => (
          <div key={c.id} className="flex items-center gap-2 rounded border px-3 py-1.5 dark:border-gray-700">
            <span>{c.passed ? "✅" : "❌"}</span>
            <span className="text-xs">{catIcon[c.category] ?? ""}</span>
            <span className={`flex-1 text-sm ${c.passed ? "" : "text-red-500"}`}>{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
