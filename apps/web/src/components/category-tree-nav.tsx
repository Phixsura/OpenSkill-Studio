"use client";

import { useState } from "react";

interface Category { id: string; label: string; icon: string; children: { id: string; label: string; icon: string }[]; }
interface CategoryTreeNavProps { categories: Category[]; activeId: string | null; onSelect: (id: string) => void; }

export function CategoryTreeNav({ categories, activeId, onSelect }: CategoryTreeNavProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <nav className="w-56 rounded-lg border border-gray-200 p-2 dark:border-gray-700">
      <h3 className="px-2 py-1 text-xs font-semibold text-gray-400">Categories</h3>
      {categories.map(cat => (
        <div key={cat.id}>
          <button onClick={() => { onSelect(cat.id); setExpanded(expanded === cat.id ? null : cat.id); }}
            className={`flex w-full items-center justify-between rounded px-2 py-1.5 text-sm ${activeId === cat.id ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400"}`}>
            <span>{cat.icon} {cat.label}</span>
            {cat.children.length > 0 && <span className="text-xs text-gray-400">{expanded === cat.id ? "▾" : "▸"}</span>}
          </button>
          {expanded === cat.id && cat.children.map(child => (
            <button key={child.id} onClick={() => onSelect(child.id)}
              className={`w-full rounded pl-6 pr-2 py-1 text-left text-sm ${activeId === child.id ? "font-semibold text-blue-700" : "text-gray-500 hover:text-gray-700"}`}>
              {child.icon} {child.label}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}
