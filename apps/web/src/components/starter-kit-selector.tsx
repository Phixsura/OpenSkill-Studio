"use client";

interface Kit { id: string; name: string; language: string; files: string[]; dependencies: string[]; }
interface StarterKitSelectorProps { kits: Kit[]; onSelect: (kitId: string) => void; }

const LANG_ICONS: Record<string, string> = { typescript: "🟦", python: "🐍" };

export function StarterKitSelector({ kits, onSelect }: StarterKitSelectorProps) {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold">Choose a Starter Kit</h3>
      <div className="grid grid-cols-2 gap-3">
        {kits.map(k => (
          <button key={k.id} onClick={() => onSelect(k.id)}
            className="rounded-lg border border-gray-200 p-4 text-left transition hover:border-blue-400 hover:shadow dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-xl">{LANG_ICONS[k.language] || "📦"}</span>
              <h4 className="font-semibold">{k.name}</h4>
            </div>
            <p className="mt-1 text-xs text-gray-400">{k.files.length} files · {k.dependencies.length} deps</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {k.dependencies.map(d => <span key={d} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">{d}</span>)}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
