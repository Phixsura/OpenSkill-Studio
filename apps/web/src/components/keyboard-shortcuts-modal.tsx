"use client";

interface Shortcut { keys: string; label: string; }
interface ShortcutCategory { category: string; shortcuts: Shortcut[]; }
interface KeyboardShortcutsModalProps { categories: ShortcutCategory[]; onClose: () => void; }

export function KeyboardShortcutsModal({ categories, onClose }: KeyboardShortcutsModalProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-2xl p-5 max-w-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">⌨️ Keyboard Shortcuts</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
      </div>
      {categories.map(c => (
        <div key={c.category} className="mb-4 last:mb-0">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">{c.category}</h4>
          <div className="space-y-1">
            {c.shortcuts.map(s => (
              <div key={s.keys} className="flex items-center justify-between text-sm py-1">
                <span>{s.label}</span>
                <kbd className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded font-mono">{s.keys}</kbd>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
