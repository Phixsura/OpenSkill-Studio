"use client";

interface Category { name: string; icon: string; count: number; }

export function MarketplaceCategoryGrid({ categories, onSelect }: { categories: Category[]; onSelect?: (name: string) => void }) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">📂 Categories</h2>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {categories.map((c) => (
          <button key={c.name} onClick={() => onSelect?.(c.name)}
            className="rounded-xl border dark:border-gray-700 p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <span className="text-2xl block">{c.icon}</span>
            <span className="font-semibold text-sm block mt-1">{c.name}</span>
            <span className="text-xs text-gray-400">{c.count} extensions</span>
          </button>
        ))}
      </div>
    </div>
  );
}
