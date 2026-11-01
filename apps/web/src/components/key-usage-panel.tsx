"use client";
interface KeyUsage { keyPreview: string; requests: number; uniqueEndpoints: number; errorRate: number; }
interface KeyUsagePanelProps { keys: KeyUsage[]; totalKeys: number; totalRequests: number; }
export function KeyUsagePanel({ keys, totalKeys, totalRequests }: KeyUsagePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Key Usage Analytics</h3>
        <span className="text-xs text-gray-400">{totalKeys} keys · {totalRequests.toLocaleString()} reqs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.keyPreview} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{k.keyPreview}</span>
            <span className="text-gray-400">{k.requests.toLocaleString()} reqs · {k.uniqueEndpoints} eps · {k.errorRate}% err</span>
          </div>
        ))}
      </div>
    </div>
  );
}
