"use client";

import { useState } from "react";

interface PaletteShade { shade: number; color: string; }
interface ColorPaletteEditorProps { primary: string; palette: PaletteShade[];
  onPrimaryChange: (color: string) => void; }

export function ColorPaletteEditor({ primary, palette, onPrimaryChange }: ColorPaletteEditorProps) {
  const [color, setColor] = useState(primary);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Brand Colors</h2>
      <div className="flex items-center gap-3">
        <input type="color" value={color} onChange={e => { setColor(e.target.value); onPrimaryChange(e.target.value); }}
          className="h-10 w-10 cursor-pointer rounded border-0" />
        <div>
          <p className="font-mono text-sm font-bold">{color}</p>
          <p className="text-xs text-gray-400">Primary Color</p>
        </div>
      </div>
      <div className="flex gap-1 overflow-hidden rounded-lg">
        {palette.map(s => (
          <div key={s.shade} className="flex-1 py-6 text-center" style={{ backgroundColor: s.color }}>
            <p className="text-[10px] font-bold text-white mix-blend-difference">{s.shade}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
