"use client";

interface PolicyRule { source: string; protocol: string; port: number | null; action: string; description: string; }
interface NetworkPolicyViewProps { ingress: PolicyRule[]; egress: PolicyRule[]; }

export function NetworkPolicyView({ ingress, egress }: NetworkPolicyViewProps) {
  const renderRules = (rules: PolicyRule[], label: string) => (
    <div>
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">{label} ({rules.length})</h4>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {rules.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs ${r.action === "allow" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
                {r.action}
              </span>
              <span className="font-mono text-xs">{r.source}</span>
            </div>
            <span className="text-xs text-gray-400">{r.protocol.toUpperCase()}{r.port ? `:${r.port}` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Network Policy</h3>
      {ingress.length > 0 && renderRules(ingress, "Ingress")}
      {egress.length > 0 && renderRules(egress, "Egress")}
    </div>
  );
}
