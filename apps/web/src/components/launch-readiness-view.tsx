"use client";

interface LaunchItem { id: string; label: string; category: string; completed: boolean; }
interface CategoryProgress { category: string; total: number; done: number; pct: number; }
interface LaunchReadinessViewProps { items: LaunchItem[]; readinessPct: number;
  launchReady: boolean; categories: CategoryProgress[]; onToggle: (id: string) => void; onLaunch: () => void; }

const catIcon: Record<string, string> = {
  design: "🎨", content: "✍️", business: "💼", engineering: "⚙️", legal: "⚖️", operations: "📊",
};

export function LaunchReadinessView({ items, readinessPct, launchReady, categories, onToggle, onLaunch }: LaunchReadinessViewProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-xl font-bold">Launch Readiness</h2>
        <p className={`text-3xl font-black ${launchReady ? "text-green-600" : "text-blue-600"}`}>{readinessPct}%</p>
      </div>
      <div className="h-3 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${launchReady ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${readinessPct}%` }} />
      </div>
      <div className="flex flex-wrap gap-2">
        {categories.map(c => (
          <span key={c.category} className={`rounded-full border px-2.5 py-1 text-xs ${c.pct === 100 ? "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/10" : "dark:border-gray-600"}`}>
            {catIcon[c.category] ?? "📁"} {c.category} {c.done}/{c.total}
          </span>
        ))}
      </div>
      <div className="space-y-1.5">
        {items.map(i => (
          <button key={i.id} onClick={() => onToggle(i.id)}
            className="flex w-full items-center gap-2 rounded border px-3 py-2 text-left text-sm dark:border-gray-700">
            <span>{i.completed ? "✅" : "⬜"}</span>
            <span className={i.completed ? "text-gray-400 line-through" : ""}>{i.label}</span>
          </button>
        ))}
      </div>
      <button onClick={onLaunch} disabled={!launchReady}
        className="w-full rounded-lg bg-green-600 py-3 text-sm font-bold text-white disabled:opacity-50">
        {launchReady ? "🚀 Launch App!" : `Complete ${items.filter(i => !i.completed).length} remaining items`}
      </button>
    </div>
  );
}
