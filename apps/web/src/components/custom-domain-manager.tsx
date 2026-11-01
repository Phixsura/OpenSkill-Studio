"use client";

interface Domain { domain: string; verified: boolean; ssl: boolean; dnsRecord: string; }
interface CustomDomainManagerProps { domains: Domain[]; onAdd: (domain: string) => void;
  onVerify: (domain: string) => void; onRemove: (domain: string) => void; }

export function CustomDomainManager({ domains, onAdd, onVerify, onRemove }: CustomDomainManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Custom Domains</h3>
        <button onClick={() => onAdd("")} className="px-3 py-1 text-xs bg-blue-500 text-white rounded-lg">Add Domain</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {domains.map(d => (
          <div key={d.domain} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono">{d.domain}</span>
                {d.verified ? (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400">✓ Verified</span>
                ) : (
                  <button onClick={() => onVerify(d.domain)} className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-700">Verify</button>
                )}
                {d.ssl && <span className="text-[10px] text-green-600">🔒 SSL</span>}
              </div>
              <button onClick={() => onRemove(d.domain)} className="text-xs text-red-500 hover:underline">Remove</button>
            </div>
            <div className="text-[10px] text-gray-400 mt-1 font-mono">{d.dnsRecord}</div>
          </div>
        ))}
        {domains.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No custom domains</div>}
      </div>
    </div>
  );
}
