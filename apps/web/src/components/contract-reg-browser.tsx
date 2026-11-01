"use client";

interface Contract { contractId: string; provider: string; consumer: string;
  version: string; fieldCount: number; status: string; }
interface ContractRegBrowserProps { contracts: Contract[]; total: number;
  providers: string[]; }

export function ContractRegBrowser({ contracts, total, providers }: ContractRegBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Contract Registry</h3>
        <span className="text-xs text-gray-400">{total} contracts · {providers.length} providers</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {contracts.map(c => (
          <div key={c.contractId} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-xs"><span className="font-mono font-medium">{c.provider}</span> → <span className="font-mono">{c.consumer}</span></div>
              <div className="text-[10px] text-gray-400">v{c.version} · {c.fieldCount} fields · {c.contractId}</div>
            </div>
            <span className="text-[10px] text-green-600">{c.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
