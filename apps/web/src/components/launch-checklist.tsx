"use client";

interface ChecklistItem { id: string; title: string; category: string;
  required: boolean; completed: boolean; }
interface LaunchChecklistProps { results: ChecklistItem[]; progressPct: number;
  readyToLaunch: boolean; missingRequired: string[];
  onToggle: (id: string) => void; onLaunch: () => void; }

export function LaunchChecklist({ results, progressPct, readyToLaunch, missingRequired, onToggle, onLaunch }: LaunchChecklistProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🚀 Launch Checklist</h3>
        <span className="text-sm font-bold">{progressPct}%</span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
        <div className={`h-full rounded-full ${readyToLaunch ? "bg-green-500" : "bg-blue-500"}`}
             style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-1.5 mb-4">
        {results.map(r => (
          <button key={r.id} onClick={() => onToggle(r.id)}
            className="w-full flex items-center gap-2 text-sm text-left py-1.5">
            <span>{r.completed ? "✅" : r.required ? "⬜" : "◻️"}</span>
            <span className={r.completed ? "line-through text-gray-400" : ""}>{r.title}</span>
            {r.required && !r.completed && <span className="text-xs text-red-500">Required</span>}
          </button>
        ))}
      </div>
      <button onClick={onLaunch} disabled={!readyToLaunch}
        className="w-full py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
        {readyToLaunch ? "🚀 Launch App" : `${missingRequired.length} required items remaining`}
      </button>
    </div>
  );
}
