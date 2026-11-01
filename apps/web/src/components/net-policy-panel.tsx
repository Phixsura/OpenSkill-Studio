"use client";

interface NetPolicy { name: string; source: string; destination: string; port: number; action: string; }
interface NetPolicyPanelProps { policies: NetPolicy[]; allowCount: number; denyCount: number; }

export function NetPolicyPanel({ policies, allowCount, denyCount }: NetPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Network Policies</h3>
        <span className="text-xs text-gray-400">{allowCount} allow · {denyCount} deny</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={p.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="font-mono">{p.source} → {p.destination}:{p.port}</div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{p.name}</span>
              <span className={p.action === "allow" ? "text-green-600" : "text-red-500"}>{p.action}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
