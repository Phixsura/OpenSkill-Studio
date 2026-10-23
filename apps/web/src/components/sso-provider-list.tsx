"use client";

interface SsoProvider { id: string; name: string; protocol: string;
  domains: string[]; enabled: boolean; verified: boolean; }
interface SsoProviderListProps { providers: SsoProvider[]; onToggle: (id: string) => void; }

export function SsoProviderList({ providers, onToggle }: SsoProviderListProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔐 SSO Providers</h3>
      <div className="space-y-3">
        {providers.map(p => (
          <div key={p.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium">{p.name}</p>
                <span className="text-xs px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 uppercase">{p.protocol}</span>
                {p.verified && <span className="text-xs text-green-600">✓ Verified</span>}
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{p.domains.join(", ")}</p>
            </div>
            <button onClick={() => onToggle(p.id)}
              className={`w-10 h-5 rounded-full transition ${p.enabled ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-4 h-4 rounded-full bg-white transition transform ${p.enabled ? "translate-x-5" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
        {providers.length === 0 && <p className="text-sm text-gray-400">No SSO providers configured</p>}
      </div>
    </div>
  );
}
