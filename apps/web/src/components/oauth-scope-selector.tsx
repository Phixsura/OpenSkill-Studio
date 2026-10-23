"use client";

interface ScopeInfo { scope: string; description: string; category: string; risk: string; }
interface ScopeGroup { category: string; scopes: ScopeInfo[]; }
interface OAuthScopeSelectorProps { groups: ScopeGroup[]; selected: Set<string>;
  onToggle: (scope: string) => void; requiresAdminConsent: boolean; }

const riskDot: Record<string, string> = { low: "bg-green-500", medium: "bg-yellow-500", high: "bg-orange-500", critical: "bg-red-500" };

export function OAuthScopeSelector({ groups, selected, onToggle, requiresAdminConsent }: OAuthScopeSelectorProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">OAuth Scopes</h2>
      {requiresAdminConsent && (
        <div className="rounded bg-yellow-50 p-2 text-center text-xs text-yellow-700 dark:bg-yellow-900/10">
          ⚠️ High-risk scopes require admin consent
        </div>
      )}
      {groups.map(g => (
        <div key={g.category}>
          <h3 className="text-sm font-medium capitalize text-gray-500">{g.category}</h3>
          <div className="mt-1 space-y-1">
            {g.scopes.map(s => (
              <label key={s.scope} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
                <input type="checkbox" checked={selected.has(s.scope)} onChange={() => onToggle(s.scope)} className="accent-blue-600" />
                <span className={`h-2 w-2 rounded-full ${riskDot[s.risk] ?? ""}`} />
                <span className="flex-1 text-sm">{s.description}</span>
                <code className="text-xs text-gray-400">{s.scope}</code>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
