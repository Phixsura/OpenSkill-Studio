"use client";

interface Filter { pattern: string; mode: string; description: string; }
interface WebhookFilterEditorProps { filters: Filter[]; onAdd: (pattern: string, mode: string) => void; onRemove: (idx: number) => void; }

export function WebhookFilterEditor({ filters, onAdd, onRemove }: WebhookFilterEditorProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Event Filters</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {filters.map((f, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono">{f.pattern}</code>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{f.mode}</span>
            </div>
            <button onClick={() => onRemove(i)} className="text-xs text-red-600 hover:underline">Remove</button>
          </div>
        ))}
        {filters.length === 0 && <p className="px-4 py-4 text-center text-sm text-gray-400">No filters — all events will be delivered</p>}
      </div>
    </div>
  );
}
