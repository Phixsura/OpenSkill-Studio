"use client";

import { useState } from "react";

interface IconEntry { name: string; svg: string; }
interface IconGalleryProps { icons: IconEntry[]; onSelect: (name: string) => void; }

export function IconGallery({ icons, onSelect }: IconGalleryProps) {
  const [search, setSearch] = useState("");
  const filtered = search ? icons.filter(i => i.name.includes(search.toLowerCase())) : icons;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Icons ({icons.length})</h3>
      </div>
      <input type="text" placeholder="Search icons..." value={search} onChange={e => setSearch(e.target.value)}
        className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <div className="grid grid-cols-6 gap-2">
        {filtered.map(i => (
          <button key={i.name} onClick={() => onSelect(i.name)} title={i.name}
            className="flex flex-col items-center gap-1 rounded-lg border p-3 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <div dangerouslySetInnerHTML={{ __html: i.svg }} className="h-6 w-6" />
            <span className="text-xs text-gray-400 truncate w-full text-center">{i.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
