"use client";
interface Policy { source: string; destination: string; timeoutMs: number; retries: number; circuitBreakThreshold: number; }
interface MeshPolicyPanelProps { policies: Policy[]; avgTimeoutMs: number; }
export function MeshPolicyPanel({ policies, avgTimeoutMs }: MeshPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Policies</h3>
        <span className="text-xs text-gray-400">{policies.length} policies · avg {avgTimeoutMs}ms timeout</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={`${p.source}→${p.destination}`} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.source} → {p.destination}</span>
            <span className="text-gray-400">{p.timeoutMs}ms · {p.retries} retries · CB@{p.circuitBreakThreshold}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
