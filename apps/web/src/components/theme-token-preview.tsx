"use client";

interface ThemeTokenPreviewProps { theme: string; tokens: Record<string, string>; }

export function ThemeTokenPreview({ theme, tokens }: ThemeTokenPreviewProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Theme Tokens — {theme}</h2>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {Object.entries(tokens).map(([name, value]) => (
          <div key={name} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <div className="h-6 w-6 rounded border" style={{ backgroundColor: value }} />
            <div>
              <p className="font-mono text-xs font-medium">{name}</p>
              <p className="font-mono text-[10px] text-gray-400">{value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
