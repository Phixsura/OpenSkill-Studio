"use client";

interface PolicyInfo { name: string; target: string; ingressCount: number;
  egressCount: number; enabled: boolean; }
interface NetworkPolicyViewerProps { policies: PolicyInfo[]; totalRules: number; }

export function NetworkPolicyViewer({ policies, totalRules }: NetworkPolicyViewerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔐 Network Policies</h3>
        <span className="text-xs text-gray-400">{policies.length} policies · {totalRules} rules</span>
      </div>
      <div className="space-y-2">
        {policies.map(p => (
          <div key={p.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm font-medium">{p.name}</p>
              <p className="text-xs text-gray-400">Target: {p.target} · {p.ingressCount} ingress · {p.egressCount} egress</p>
            </div>
            <span className={`w-2.5 h-2.5 rounded-full ${p.enabled ? "bg-green-500" : "bg-gray-300"}`} />
          </div>
        ))}
      </div>
    </div>
  );
}
