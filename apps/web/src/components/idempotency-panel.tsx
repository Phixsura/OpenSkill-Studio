"use client";

interface IdempKeyInfo { key: string; hasResponse: boolean; ageSeconds: number; }
interface IdempotencyPanelProps { keys: IdempKeyInfo[]; activeKeys: number; ttlSeconds: number; }

export function IdempotencyPanel({ keys, activeKeys, ttlSeconds }: IdempotencyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Idempotency Keys</h3>
        <span className="text-xs text-gray-400">{activeKeys} active · {ttlSeconds}s TTL</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.key} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{k.key}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{k.ageSeconds}s ago</span>
              <span className={k.hasResponse ? "text-green-600" : "text-yellow-600"}>
                {k.hasResponse ? "stored" : "pending"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
