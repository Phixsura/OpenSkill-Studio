"use client";

interface PublishCheck { check: string; label: string; pass: boolean; }
interface PublishFlowProps { checks: PublishCheck[]; canPublish: boolean; score: number;
  version: string; onPublish: () => void; }

export function PublishFlow({ checks, canPublish, score, version, onPublish }: PublishFlowProps) {
  return (
    <div className="mx-auto max-w-lg space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold">Publish v{version}</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${canPublish ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {score}% ready
        </span>
      </div>
      <div className="space-y-1">
        {checks.map(c => (
          <div key={c.check} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <span className="text-sm">{c.label}</span>
            <span className={c.pass ? "text-green-600" : "text-red-600"}>{c.pass ? "✓" : "✗"}</span>
          </div>
        ))}
      </div>
      <button onClick={onPublish} disabled={!canPublish}
        className="w-full rounded-lg bg-green-600 py-3 text-sm font-medium text-white disabled:opacity-30">
        {canPublish ? "🚀 Publish to Marketplace" : "Complete all checks first"}
      </button>
    </div>
  );
}
