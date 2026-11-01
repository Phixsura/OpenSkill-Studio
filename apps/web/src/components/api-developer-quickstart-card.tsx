"use client";

interface StepInfo { step_id: string; title: string; completed: boolean; }
interface Props { language: string; steps: StepInfo[]; completionPct: number; appName: string; }

export default function APIDeveloperQuickstartCard({ language, steps, completionPct, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Quickstart</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {language}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{completionPct}%</span>
      </div>
      <div className="mb-2 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-green-500" style={{ width: `${completionPct}%` }} />
      </div>
      <div className="space-y-0.5">
        {steps.map((s) => (
          <div key={s.step_id} className="flex items-center gap-2 text-[11px]">
            <span className={s.completed ? "text-green-500" : "text-gray-300"}>{s.completed ? "✓" : "○"}</span>
            <span className={s.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{s.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
