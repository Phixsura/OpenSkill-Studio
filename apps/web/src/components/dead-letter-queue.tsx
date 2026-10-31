"use client";

interface DeadLetter { eventId: string; eventType: string; url: string; error: string; attempts: number; deadAt: string; }

interface DeadLetterQueueProps { items: DeadLetter[]; onRetry?: (eventId: string) => void; onPurge?: () => void; }

export function DeadLetterQueue({ items, onRetry, onPurge }: DeadLetterQueueProps) {
  if (items.length === 0) return <p className="py-3 text-center text-sm text-green-600">✅ No dead letters</p>;
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm text-red-600">{items.length} failed event{items.length !== 1 ? "s" : ""}</span>
        {onPurge && <button onClick={onPurge} className="text-xs text-red-500">Purge All</button>}
      </div>
      <div className="space-y-2">
        {items.map(dl => (
          <div key={dl.eventId} className="rounded border border-red-200 p-2 text-sm dark:border-red-800">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs">{dl.eventType}</span>
              {onRetry && <button onClick={() => onRetry(dl.eventId)} className="text-xs text-blue-600">Retry</button>}
            </div>
            <p className="text-xs text-red-600">{dl.error} ({dl.attempts} attempts)</p>
          </div>
        ))}
      </div>
    </div>
  );
}
