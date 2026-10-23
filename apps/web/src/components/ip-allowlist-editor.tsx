"use client";

interface IpRule { cidr: string; label: string; valid: boolean; numHosts: number; }
interface IpAllowlistEditorProps { rules: IpRule[]; onAdd: (cidr: string, label: string) => void;
  onRemove: (cidr: string) => void; }

export function IpAllowlistEditor({ rules, onAdd, onRemove }: IpAllowlistEditorProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">IP Allowlist</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {rules.map(r => (
          <div key={r.cidr} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono">{r.cidr}</code>
                {!r.valid && <span className="text-xs text-red-500">Invalid</span>}
              </div>
              {r.label && <p className="text-xs text-gray-400">{r.label}</p>}
              {r.valid && <p className="text-xs text-gray-400">{r.numHosts.toLocaleString()} hosts</p>}
            </div>
            <button onClick={() => onRemove(r.cidr)} className="text-xs text-red-600 hover:underline">Remove</button>
          </div>
        ))}
        {rules.length === 0 && <p className="px-4 py-6 text-center text-sm text-gray-400">No rules — all IPs allowed</p>}
      </div>
    </div>
  );
}
