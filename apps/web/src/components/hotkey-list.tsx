"use client";

interface Shortcut { combo: string; action: string; category: string; enabled: boolean; }
interface HotkeyListProps { shortcuts: Shortcut[]; categories: string[]; }

export function HotkeyList({ shortcuts, categories }: HotkeyListProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Keyboard Shortcuts</h3>
      {categories.map(cat => (
        <div key={cat}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-2">{cat}</p>
          <div className="space-y-1">
            {shortcuts.filter(s => s.category === cat).map(s => (
              <div key={s.combo + s.action} className={`flex items-center justify-between py-1.5 ${!s.enabled ? "opacity-40" : ""}`}>
                <span className="text-sm">{s.action}</span>
                <kbd className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono dark:bg-gray-800">{s.combo}</kbd>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
