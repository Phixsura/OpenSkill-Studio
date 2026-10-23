"use client";

interface SetupStep { id: string; title: string; description: string; required: boolean; completed: boolean; }
interface SetupProgressCardProps { steps: SetupStep[]; progressPct: number;
  readyToPublish: boolean; nextStep: SetupStep | null; onComplete: (id: string) => void; }

export function SetupProgressCard({ steps, progressPct, readyToPublish, nextStep, onComplete }: SetupProgressCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">App Setup</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${readyToPublish ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {readyToPublish ? "✓ Ready to publish" : `${progressPct}% complete`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700 mb-4">
        <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.id} className={`flex items-center gap-2 ${s.completed ? "opacity-50" : ""}`}>
            <span className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${s.completed ? "bg-green-500 text-white" : "border dark:border-gray-600"}`}>
              {s.completed ? "✓" : ""}
            </span>
            <div className="flex-1">
              <span className={`text-sm ${s.completed ? "line-through text-gray-400" : "font-medium"}`}>{s.title}</span>
              {s.required && !s.completed && <span className="ml-1 text-xs text-red-500">*</span>}
            </div>
            {!s.completed && <button onClick={() => onComplete(s.id)} className="text-xs text-blue-600">Start</button>}
          </div>
        ))}
      </div>
    </div>
  );
}
