"use client";

interface Secret { key: string; createdAt?: string; }
interface SecretsManagementProps { secrets: Secret[]; canAdd: boolean; remaining: number; onAdd?: () => void; onDelete?: (key: string) => void; }

export function SecretsManagement({ secrets, canAdd, remaining, onAdd, onDelete }: SecretsManagementProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">🔐 Secrets ({secrets.length})</h4>
        {canAdd && onAdd && <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">+ Add Secret</button>}
      </div>
      {secrets.length === 0 ? <p className="text-sm text-gray-400">No secrets configured</p> : (
        <ul className="space-y-1">{secrets.map(s => (
          <li key={s.key} className="flex items-center justify-between rounded bg-gray-50 p-2 dark:bg-gray-800">
            <code className="text-sm font-semibold">{s.key}</code>
            {onDelete && <button onClick={() => onDelete(s.key)} className="text-xs text-red-500">Delete</button>}
          </li>
        ))}</ul>
      )}
      <p className="mt-2 text-xs text-gray-400">{remaining} remaining</p>
    </div>
  );
}
