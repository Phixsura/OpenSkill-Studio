"use client";

interface Step { index: number; label: string; completed: boolean; }
interface StepProgressBarProps { title: string; steps: Step[]; pct: number;
  completedCount: number; total: number; }

export function StepProgressBar({ title, steps, pct, completedCount, total }: StepProgressBarProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">{title}</h3>
        <span className="text-sm font-bold">{pct}%</span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-4 overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
      </div>
      <div className="flex gap-1">
        {steps.map(s => (
          <div key={s.index} className="flex-1 text-center">
            <div className={`w-6 h-6 rounded-full mx-auto flex items-center justify-center text-xs font-bold ${
              s.completed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-500"
            }`}>{s.completed ? "✓" : s.index + 1}</div>
            <p className="text-[10px] text-gray-400 mt-1">{s.label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-2">{completedCount}/{total} complete</p>
    </div>
  );
}
