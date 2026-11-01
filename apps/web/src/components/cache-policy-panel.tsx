"use client";
interface Policy { endpoint: string; ttl: number; cacheable: boolean; varyBy: string[]; }
interface CachePolicyPanelProps { policies: Policy[]; cacheableCount: number; }
export function CachePolicyPanel({ policies, cacheableCount }: CachePolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💨 Cache Policies</h3>
        <span className="text-xs text-gray-400">{cacheableCount}/{policies.length} cacheable</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={p.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.endpoint}</span>
            <span className={p.cacheable ? "text-green-600" : "text-gray-400"}>
              {p.cacheable ? `${p.ttl}s${p.varyBy.length > 0 ? ` · vary: ${p.varyBy.join(",")}` : ""}` : "no-store"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
