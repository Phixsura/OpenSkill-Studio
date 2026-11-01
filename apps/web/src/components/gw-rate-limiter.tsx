"use client";

interface ClientLimit { clientId: string; rpm: number; current: number; blocked: number; }
interface GwRateLimiterProps { clients: ClientLimit[]; totalBlocked: number; }

export function GwRateLimiter({ clients, totalBlocked }: GwRateLimiterProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Gateway Rate Limits</h3>
        <span className="text-xs text-gray-400">{clients.length} clients · {totalBlocked} blocked</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {clients.map(c => {
          const pct = Math.round((c.current / Math.max(c.rpm, 1)) * 100);
          return (
            <div key={c.clientId} className="px-4 py-2">
              <div className="flex justify-between text-xs mb-0.5">
                <span className="font-mono">{c.clientId}</span>
                <span className="text-gray-400">{c.current}/{c.rpm} rpm{c.blocked > 0 ? ` · ${c.blocked} blocked` : ""}</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${pct > 90 ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
