"use client";

interface DevToolkitPanelProps { tools: { id: string; name: string; icon: string; description: string }[];
  onSelect: (id: string) => void; }

export function DevToolkitPanel({ tools, onSelect }: DevToolkitPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🧰 Developer Toolkit</h3>
      <div className="grid grid-cols-2 gap-2">
        {tools.map(t => (
          <button key={t.id} onClick={() => onSelect(t.id)}
            className="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-left transition">
            <span className="text-xl">{t.icon}</span>
            <div>
              <p className="text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-400">{t.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
