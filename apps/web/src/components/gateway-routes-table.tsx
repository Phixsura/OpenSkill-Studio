"use client";

interface GatewayRoute { path: string; upstream: string; methods: string[];
  authRequired: boolean; rateLimit: number; }
interface GatewayRoutesTableProps { routes: GatewayRoute[]; total: number;
  rateLimited: number; }

export function GatewayRoutesTable({ routes, total, rateLimited }: GatewayRoutesTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 API Gateway</h3>
        <span className="text-xs text-gray-400">{total} routes · {rateLimited} rate-limited</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map(r => (
          <div key={r.path} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono">{r.path}</span>
                {!r.authRequired && <span className="text-[10px] text-yellow-600">public</span>}
              </div>
              <div className="text-[10px] text-gray-400">→ {r.upstream}</div>
            </div>
            <div className="flex gap-1">
              {r.methods.map(m => (
                <span key={m} className="px-1.5 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded font-mono">{m}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
