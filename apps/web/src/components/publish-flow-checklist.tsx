"use client";

interface Check { key: string; label: string; passed: boolean; required: boolean; }
interface PublishFlowChecklistProps { checks: Check[]; passedCount: number; totalCount: number; pct: number;
  readyToPublish: boolean; submitLabel: string; onSubmit: () => void; }

export function PublishFlowChecklist({ checks, passedCount, totalCount, pct, readyToPublish, submitLabel, onSubmit }: PublishFlowChecklistProps) {
  return (
    <div className="mx-auto max-w-lg space-y-4">
      <div>
        <h2 className="text-lg font-bold">Publish Checklist</h2>
        <div className="mt-2 flex items-center gap-3">
          <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-full rounded-full ${pct === 100 ? "bg-green-500" : "bg-blue-600"}`} style={{ width: `${pct}%` }} />
          </div>
          <span className="text-sm font-medium">{passedCount}/{totalCount}</span>
        </div>
      </div>
      <ul className="space-y-2">
        {checks.map(c => (
          <li key={c.key} className={`flex items-center gap-3 rounded-lg border p-3 ${
            c.passed ? "border-green-200 dark:border-green-800" : c.required ? "border-red-200 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
            <span className="text-lg">{c.passed ? "✅" : c.required ? "❌" : "⬜"}</span>
            <span className={`flex-1 text-sm ${c.passed ? "line-through opacity-50" : "font-medium"}`}>{c.label}</span>
            {c.required && !c.passed && <span className="text-xs text-red-500">Required</span>}
          </li>
        ))}
      </ul>
      <button onClick={onSubmit} disabled={!readyToPublish}
        className="w-full rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white disabled:opacity-50">
        {submitLabel}
      </button>
    </div>
  );
}
