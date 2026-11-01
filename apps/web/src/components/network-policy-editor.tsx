"use client";

interface Rule { direction: string; target: string; port: number | null; protocol: string; action: string; }
interface NetworkPolicyEditorProps { rules: Rule[]; onAdd: (rule: Rule) => void; onRemove: (index: number) => void; }

export function NetworkPolicyEditor({ rules, onAdd, onRemove }: NetworkPolicyEditorProps) {
  const egress = rules.filter(r => r.direction === "egress");
  const ingress = rules.filter(r => r.direction === "ingress");

  const renderRules = (list: Rule[], label: string) => (
    <div>
      <h3 className="text-sm font-medium text-gray-500">{label}</h3>
      {list.length === 0 ? (
        <p className="mt-1 text-xs text-gray-400">No {label.toLowerCase()} rules</p>
      ) : (
        <div className="mt-1 space-y-1">
          {list.map((r, i) => {
            const globalIdx = rules.indexOf(r);
            return (
              <div key={i} className="flex items-center justify-between rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-700">
                <span className={r.action === "allow" ? "text-green-500" : "text-red-500"}>{r.action.toUpperCase()}</span>
                <span>{r.target}</span>
                <span className="text-gray-400">{r.protocol}:{r.port ?? "*"}</span>
                <button onClick={() => onRemove(globalIdx)} className="text-red-400">×</button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Network Policy</h2>
      {renderRules(egress, "Egress (Outbound)")}
      {renderRules(ingress, "Ingress (Inbound)")}
    </div>
  );
}
