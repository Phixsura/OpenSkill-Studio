"use client";

interface Shortcut { key: string; label: string; scope: string; }
interface KeyboardShortcutsDialogProps { shortcuts: Shortcut[]; onClose: () => void; }

export function KeyboardShortcutsDialog({ shortcuts, onClose }: KeyboardShortcutsDialogProps) {
  const scopes = [...new Set(shortcuts.map(s => s.scope))];
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold">Keyboard Shortcuts</h2>
          <button onClick={onClose} className="text-gray-400">✕</button>
        </div>
        {scopes.map(scope => (
          <div key={scope} className="mt-4">
            <h3 className="text-xs font-semibold uppercase text-gray-400">{scope}</h3>
            <ul className="mt-1 space-y-1">
              {shortcuts.filter(s => s.scope === scope).map(s => (
                <li key={s.key} className="flex items-center justify-between text-sm">
                  <span>{s.label}</span>
                  <kbd className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono dark:bg-gray-700">{s.key}</kbd>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
