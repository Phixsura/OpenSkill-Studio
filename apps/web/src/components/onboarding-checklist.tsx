"use client";

interface Task { id: string; title: string; description: string; completed: boolean;
  action_url: string | null; icon: string; required: boolean; }
interface OnboardingChecklistProps { tasks: Task[]; greeting: string; progressPct: number;
  onComplete: (id: string) => void; }

export function OnboardingChecklist({ tasks, greeting, progressPct, onComplete }: OnboardingChecklistProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h2 className="text-lg font-bold">{greeting}</h2>
      <p className="mt-1 text-sm text-gray-500">Complete these steps to get started</p>
      <div className="mt-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-400">{progressPct}% complete</p>
      <ul className="mt-4 space-y-3">
        {tasks.map(t => (
          <li key={t.id} className="flex items-start gap-3">
            <button onClick={() => !t.completed && onComplete(t.id)}
              className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border text-xs ${t.completed ? "bg-green-500 border-green-500 text-white" : "dark:border-gray-600"}`}>
              {t.completed && "✓"}
            </button>
            <div>
              <p className={`text-sm font-medium ${t.completed ? "line-through text-gray-400" : ""}`}>{t.title}</p>
              {t.description && <p className="text-xs text-gray-500">{t.description}</p>}
              {!t.required && <span className="text-xs text-gray-400 italic">Optional</span>}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
