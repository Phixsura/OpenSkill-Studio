"use client";

interface Shade { shade: number; hex: string; }
interface ColorSwatchGridProps { baseColor: string; shades: Shade[]; }

export function ColorSwatchGrid({ baseColor, shades }: ColorSwatchGridProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🎨 Color Palette</h3>
      <p className="text-xs text-gray-400 mb-3">Base: {baseColor}</p>
      <div className="flex gap-1 rounded-lg overflow-hidden">
        {shades.map(s => (
          <div key={s.shade} className="flex-1 flex flex-col items-center">
            <div className="w-full h-12" style={{ backgroundColor: s.hex }} />
            <span className="text-[10px] text-gray-400 mt-1">{s.shade}</span>
            <span className="text-[9px] font-mono text-gray-300">{s.hex}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
