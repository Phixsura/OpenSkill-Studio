"use client";

interface ThemePreset { name: string; previewBg: string; previewPrimary: string; }
interface ThemeSwitcherProps { presets: ThemePreset[]; current: string;
  onSelect: (name: string) => void; }

export function ThemeSwitcher({ presets, current, onSelect }: ThemeSwitcherProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🎨 Theme</h3>
      <div className="flex gap-3">
        {presets.map(p => (
          <button key={p.name} onClick={() => onSelect(p.name)}
            className={`flex flex-col items-center gap-1.5 p-3 rounded-lg border-2 transition ${
              p.name === current ? "border-blue-500" : "border-transparent hover:border-gray-200 dark:hover:border-gray-600"
            }`}>
            <div className="w-12 h-12 rounded-lg overflow-hidden flex">
              <div className="w-1/2 h-full" style={{ backgroundColor: p.previewBg }} />
              <div className="w-1/2 h-full" style={{ backgroundColor: p.previewPrimary }} />
            </div>
            <span className="text-xs capitalize">{p.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
