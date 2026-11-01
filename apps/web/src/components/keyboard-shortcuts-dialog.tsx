"use client";

interface Shortcut { combo: string; action: string; context: string; description: string; }
interface KeyboardShortcutsDialogProps { byContext: Record<string, Shortcut[]>; onClose: () => void; }

export function KeyboardShortcutsDialog({ byContext, onClose }: KeyboardShortcutsDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">Keyboard Shortcuts</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        {Object.entries(byContext).map(([ctx, shortcuts]) => (
          <div key={ctx} className="mb-4">
            <p className="text-xs font-semibold text-gray-400 uppercase mb-2">{ctx}</p>
            {shortcuts.map((s, i) => (
              <div key={i} className="flex items-center justify-between py-1.5">
                <span className="text-sm">{s.action}</span>
                <kbd className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono dark:bg-gray-800">{s.combo}</kbd>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
