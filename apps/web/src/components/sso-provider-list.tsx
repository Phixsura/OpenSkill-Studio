"use client";

interface SsoProvider { name: string; protocol: string; status: string; clientId?: string; }
interface SsoProviderListProps { providers: SsoProvider[]; active: number;
  onAdd: () => void; onToggle: (name: string) => void; }

const PROTO_BADGE: Record<string, string> = {
  oauth2: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
  saml: "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
  oidc: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
};

export function SsoProviderList({ providers, active, onAdd, onToggle }: SsoProviderListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 SSO Providers</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{active}/{providers.length} active</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {providers.map(p => (
          <div key={p.name} className={`flex items-center justify-between px-4 py-3 ${p.status !== "active" ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{p.name}</span>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${PROTO_BADGE[p.protocol] ?? ""}`}>{p.protocol}</span>
            </div>
            <button onClick={() => onToggle(p.name)}
              className={`text-xs ${p.status === "active" ? "text-green-600" : "text-gray-400"}`}>
              {p.status === "active" ? "● Active" : "○ Disabled"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
