"use client";

interface Category { id: string; label: string; icon: string; count: number; description?: string; }
interface CategoryGridProps { categories: Category[]; onSelect: (id: string) => void; }

export function CategoryGrid({ categories, onSelect }: CategoryGridProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {categories.map(c => (
        <button key={c.id} onClick={() => onSelect(c.id)}
          className="rounded-xl border dark:border-gray-700 p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-800 transition">
          <p className="text-2xl mb-1">{c.icon}</p>
          <p className="text-sm font-medium">{c.label}</p>
          <p className="text-xs text-gray-400">{c.count} apps</p>
        </button>
      ))}
    </div>
  );
}
