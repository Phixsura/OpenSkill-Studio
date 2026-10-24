"use client";

interface TransformRule { action: string; path: string; to?: string; value?: unknown; }
interface WebhookTransformEditorProps { rules: TransformRule[];
  onAdd: (rule: TransformRule) => void; onRemove: (index: number) => void; onTest: () => void; }

const actionLabels: Record<string, string> = { rename: "✏️ Rename", remove: "🗑️ Remove", add: "➕ Add", mask: "🔒 Mask" };

export function WebhookTransformEditor({ rules, onAdd, onRemove, onTest }: WebhookTransformEditorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Webhook Transforms</h2>
        <button onClick={onTest} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Test</button>
      </div>
      {rules.length === 0 ? (
        <p className="text-sm text-gray-400">No transform rules — payload delivered as-is</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r, i) => (
            <div key={i} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div className="flex items-center gap-2 text-sm">
                <span>{actionLabels[r.action] ?? r.action}</span>
                <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{r.path}</code>
                {r.to && <><span className="text-gray-400">→</span><code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{r.to}</code></>}
              </div>
              <button onClick={() => onRemove(i)} className="text-xs text-red-500">×</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
