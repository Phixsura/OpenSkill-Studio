"use client";

interface Scope { scope: string; description: string; category: string; }
interface OAuthScopeSelectorProps { scopes: Scope[]; selected: string[];
  onToggle: (scope: string) => void; hasAdmin: boolean; }

const CAT_COLORS: Record<string, string> = {
  user: "bg-blue-100 text-blue-700", apps: "bg-green-100 text-green-700",
  billing: "bg-yellow-100 text-yellow-700", admin: "bg-red-100 text-red-700",
  analytics: "bg-purple-100 text-purple-700",
};

export function OAuthScopeSelector({ scopes, selected, onToggle, hasAdmin }: OAuthScopeSelectorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 OAuth Scopes</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{selected.length} selected</span>
          {hasAdmin && <span className="text-red-500">⚠ Admin</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {scopes.map(s => {
          const isSelected = selected.includes(s.scope);
          return (
            <button key={s.scope} onClick={() => onToggle(s.scope)}
              className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 text-left">
              <div className="flex items-center gap-2">
                <span className={`w-4 h-4 rounded border ${isSelected ? "bg-blue-500 border-blue-500" : "border-gray-300"} flex items-center justify-center text-[10px] text-white`}>
                  {isSelected ? "✓" : ""}
                </span>
                <span className="text-sm font-mono">{s.scope}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{s.description}</span>
                <span className={`px-1.5 py-0.5 text-[10px] rounded ${CAT_COLORS[s.category] ?? ""}`}>{s.category}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
