"use client";

interface CheckItem { id: string; label: string; category: string; passed: boolean; auto_check: boolean; }
interface PublishChecklistPanelProps { items: CheckItem[]; canPublish: boolean;
  readinessPct: number; blocking: string[]; onPublish: () => void; onRunChecks: () => void; }

const catLabel: Record<string, { icon: string; label: string }> = {
  required: { icon: "🔴", label: "Required" },
  quality: { icon: "🟡", label: "Quality" },
  recommended: { icon: "🟢", label: "Recommended" },
};

export function PublishChecklistPanel({ items, canPublish, readinessPct, blocking, onPublish, onRunChecks }: PublishChecklistPanelProps) {
  const grouped = Object.entries(catLabel).map(([cat, info]) => ({
    ...info, category: cat, items: items.filter(i => i.category === cat),
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Publish Checklist</h2>
        <span className="text-sm font-bold">{readinessPct}%</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${readinessPct === 100 ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${readinessPct}%` }} />
      </div>
      {grouped.map(g => (
        <div key={g.category}>
          <h3 className="text-xs font-medium text-gray-400">{g.icon} {g.label}</h3>
          <div className="mt-1 space-y-1">
            {g.items.map(i => (
              <div key={i.id} className="flex items-center gap-2 text-sm">
                <span>{i.passed ? "✅" : "⬜"}</span>
                <span className={i.passed ? "text-gray-400" : ""}>{i.label}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className="flex gap-2">
        <button onClick={onRunChecks} className="flex-1 rounded border py-2 text-sm dark:border-gray-600">Run Checks</button>
        <button onClick={onPublish} disabled={!canPublish}
          className="flex-1 rounded bg-green-600 py-2 text-sm text-white disabled:opacity-50">
          {canPublish ? "🚀 Publish" : `Fix ${blocking.length} issues`}
        </button>
      </div>
    </div>
  );
}
