"use client";

interface Theme { id: string; name: string; preview: Record<string, string>; }
interface ThemeSwitcherProps { themes: Theme[]; activeTheme: string; onSwitch: (id: string) => void; }

export function ThemeSwitcher({ themes, activeTheme, onSwitch }: ThemeSwitcherProps) {
  return (
    <div className="flex gap-2">
      {themes.map(t => (
        <button key={t.id} onClick={() => onSwitch(t.id)}
          className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${activeTheme === t.id ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 dark:border-gray-700"}`}>
          <span className="flex gap-0.5">
            {Object.values(t.preview).slice(0, 3).map((c, i) => (
              <span key={i} className="h-3 w-3 rounded-full" style={{ backgroundColor: c }} />
            ))}
          </span>
          <span>{t.name}</span>
        </button>
      ))}
    </div>
  );
}
