"use client";
interface Contract { name: string; versions: number; latest: string; }
interface ContractRegPanelProps { contracts: Contract[]; totalVersions: number; }
export function ContractRegPanel({ contracts, totalVersions }: ContractRegPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Contract Registry</h3>
        <span className="text-xs text-gray-400">{contracts.length} contracts · {totalVersions} versions</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {contracts.map(c => (
          <div key={c.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.name}</span>
            <span className="text-gray-400">v{c.latest} · {c.versions} versions</span>
          </div>
        ))}
      </div>
    </div>
  );
}
