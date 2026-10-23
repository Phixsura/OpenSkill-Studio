"use client";

interface Condition { field: string; operator: string; value: string; }
interface WebhookFilterBuilderProps { conditions: Condition[]; onAdd: (c: Condition) => void; onRemove: (index: number) => void; }

export function WebhookFilterBuilder({ conditions, onAdd, onRemove }: WebhookFilterBuilderProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Webhook Filters</h3>
      <p className="mt-1 text-xs text-gray-400">Only deliver webhooks matching these conditions.</p>
      {conditions.length === 0 ? <p className="mt-3 text-sm text-gray-400">No filters — all events delivered.</p> : (
        <ul className="mt-3 space-y-1">
          {conditions.map((c, i) => (
            <li key={i} className="flex items-center justify-between rounded bg-gray-50 px-3 py-1.5 text-xs dark:bg-gray-800">
              <code>{c.field} {c.operator} {c.value}</code>
              <button onClick={() => onRemove(i)} className="text-red-500">✕</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
