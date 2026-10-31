"use client";

interface Shortcut { key: string; action: string; label: string; category: string; }
interface KeyboardShortcutHelpProps { shortcuts: Shortcut[]; categories: string[]; onClose: () => void; }

export function KeyboardShortcutHelp({ shortcuts, categories, onClose }: KeyboardShortcutHelpProps) {
  const grouped = categories.map(cat => ({
    category: cat,
    items: shortcuts.filter(s => s.category === cat),
  }));

  return (
    <div className="rounded-lg border bg-white p-5 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Keyboard Shortcuts</h2>
        <button onClick={onClose} className="text-gray-400">✕</button>
      </div>
      <div className="mt-4 space-y-4">
        {grouped.map(g => (
          <div key={g.category}>
            <h3 className="text-xs font-medium uppercase text-gray-400">{g.category}</h3>
            <div className="mt-1 space-y-1">
              {g.items.map(s => (
                <div key={s.key} className="flex items-center justify-between py-1">
                  <span className="text-sm">{s.label}</span>
                  <kbd className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs dark:bg-gray-800">{s.key}</kbd>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
