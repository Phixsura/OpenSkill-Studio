"use client";

interface IdempotencyKeyViewerProps { trackedKeys: number; ttlSec: number;
  recentKeys: { key: string; age: string; }[]; }

export function IdempotencyKeyViewer({ trackedKeys, ttlSec, recentKeys }: IdempotencyKeyViewerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔑 Idempotency Keys</h3>
      <div className="flex gap-4 mb-4 text-sm">
        <div className="text-center">
          <p className="text-lg font-bold">{trackedKeys}</p>
          <p className="text-xs text-gray-400">Active Keys</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-bold">{ttlSec}s</p>
          <p className="text-xs text-gray-400">TTL</p>
        </div>
      </div>
      {recentKeys.length > 0 && (
        <div className="space-y-1">
          {recentKeys.map(k => (
            <div key={k.key} className="flex justify-between text-xs bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
              <span className="font-mono truncate max-w-[200px]">{k.key}</span>
              <span className="text-gray-400">{k.age} ago</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
