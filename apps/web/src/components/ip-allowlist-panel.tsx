"use client";

interface IpRule { name: string; cidr: string; description: string; }
interface IpAllowlistPanelProps { rules: IpRule[]; }

export function IpAllowlistPanel({ rules }: IpAllowlistPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ IP Allowlist</h3>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>
      {rules.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {rules.map(r => (
            <div key={r.name} className="flex items-center justify-between px-4 py-2 text-xs">
              <div>
                <span className="font-semibold">{r.name}</span>
                {r.description && <span className="text-gray-400 ml-2">{r.description}</span>}
              </div>
              <span className="font-mono text-blue-500">{r.cidr}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-yellow-600 text-center">⚠ No rules — all IPs denied</div>
      )}
    </div>
  );
}
