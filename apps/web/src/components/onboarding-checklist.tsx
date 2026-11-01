"use client";

interface ChecklistItem { itemId: string; title: string; description: string; completed: boolean; required: boolean; }
interface Progress { total: number; completed: number; percentage: number; }

export function OnboardingChecklist({ items, progress, onComplete }: {
  items: ChecklistItem[]; progress: Progress; onComplete?: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="font-bold">Getting Started</span>
          <span className="text-gray-500">{progress.completed}/{progress.total} ({progress.percentage}%)</span>
        </div>
        <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${progress.percentage}%` }} />
        </div>
      </div>
      <div className="space-y-1.5">
        {items.map(item => (
          <button key={item.itemId} onClick={() => !item.completed && onComplete?.(item.itemId)}
            className={`w-full text-left border rounded-xl p-3 flex items-start gap-3 ${item.completed ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <span className={`mt-0.5 ${item.completed ? "text-green-500" : "text-gray-300"}`}>{item.completed ? "✅" : "⬜"}</span>
            <div>
              <span className={`text-sm font-medium ${item.completed ? "line-through text-gray-400" : ""}`}>{item.title}</span>
              {item.required && !item.completed && <span className="text-xs text-red-400 ml-1">required</span>}
              <p className="text-xs text-gray-500">{item.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
