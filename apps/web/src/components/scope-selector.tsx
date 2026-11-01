"use client";

interface Scope { id: string; description: string; category: string; dangerous: boolean; }
interface ScopeSelectorProps { scopes: Scope[]; selected: Set<string>; onToggle: (id: string) => void; }

export function ScopeSelector({ scopes, selected, onToggle }: ScopeSelectorProps) {
  const grouped = scopes.reduce<Record<string, Scope[]>>((acc, s) => {
    (acc[s.category] ??= []).push(s); return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Permissions</h3>
      {Object.entries(grouped).map(([cat, items]) => (
        <div key={cat}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-2">{cat}</p>
          <div className="space-y-1">
            {items.map(s => (
              <label key={s.id} className="flex items-center gap-3 rounded-lg border px-3 py-2 cursor-pointer dark:border-gray-700">
                <input type="checkbox" checked={selected.has(s.id)} onChange={() => onToggle(s.id)} className="accent-blue-600" />
                <div className="flex-1">
                  <span className="text-sm font-mono">{s.id}</span>
                  <p className="text-xs text-gray-400">{s.description}</p>
                </div>
                {s.dangerous && <span className="text-xs text-red-500">⚠ Dangerous</span>}
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
