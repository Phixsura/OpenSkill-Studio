"use client";

interface Condition { field: string; operator: string; value: unknown; }
interface WebhookFilterBuilderProps { name: string; conditions: Condition[];
  onAdd: () => void; onRemove: (index: number) => void; onSave: () => void; }

const opLabels: Record<string, string> = {
  eq: "equals", ne: "not equals", contains: "contains", starts_with: "starts with",
  gt: ">", lt: "<", in: "in list", exists: "exists",
};

export function WebhookFilterBuilder({ name, conditions, onAdd, onRemove, onSave }: WebhookFilterBuilderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Webhook Filter: {name}</h2>
        <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Add Condition</button>
      </div>
      {conditions.length === 0 ? (
        <p className="text-sm text-gray-400">No conditions — all events delivered</p>
      ) : (
        <div className="space-y-1.5">
          {conditions.map((c, i) => (
            <div key={i} className="flex items-center gap-2 rounded border px-3 py-2 font-mono text-xs dark:border-gray-700">
              <span className="text-blue-500">{c.field}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">{opLabels[c.operator] ?? c.operator}</span>
              <span className="text-green-500">{String(c.value)}</span>
              <button onClick={() => onRemove(i)} className="ml-auto text-red-400">×</button>
            </div>
          ))}
        </div>
      )}
      <button onClick={onSave} className="w-full rounded bg-green-600 py-2 text-sm text-white">Save Filter</button>
    </div>
  );
}
