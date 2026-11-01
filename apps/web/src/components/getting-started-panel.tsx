"use client";

interface ChecklistItem { itemId: string; title: string; description: string; helpUrl: string; completed: boolean; }
interface Progress { completed: number; total: number; percent: number; nextStep: string | null; allDone: boolean; }

export function GettingStartedPanel({
  items, progress, onComplete,
}: {
  items: ChecklistItem[]; progress: Progress;
  onComplete?: (itemId: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚀 Getting Started</h2>
        <span className="text-sm text-gray-500">{progress.completed}/{progress.total}</span>
      </div>

      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${progress.allDone ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${progress.percent}%` }} />
      </div>

      {progress.allDone && (
        <div className="text-center py-4">
          <span className="text-3xl">🎉</span>
          <p className="font-bold mt-1">You're all set!</p>
        </div>
      )}

      <div className="space-y-1">
        {items.map((item) => (
          <div key={item.itemId} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center gap-3 ${item.completed ? "opacity-60" : ""}`}>
            <button onClick={() => !item.completed && onComplete?.(item.itemId)}
              className={`w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 ${
                item.completed ? "bg-green-500 border-green-500 text-white" : "border-gray-300 dark:border-gray-600"
              }`}>
              {item.completed && "✓"}
            </button>
            <div className="flex-1">
              <span className={`font-semibold text-sm ${item.completed ? "line-through" : ""}`}>{item.title}</span>
              <p className="text-xs text-gray-500">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
