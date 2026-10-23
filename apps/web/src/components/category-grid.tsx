"use client";

interface Category { id: string; name: string; icon: string; description: string; count: number; }
interface CategoryGridProps { categories: Category[]; totalApps: number; onSelect: (id: string) => void; }

export function CategoryGrid({ categories, totalApps, onSelect }: CategoryGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📂 Browse Categories</h2>
        <span className="text-xs text-gray-400">{categories.length} categories · {totalApps.toLocaleString()} apps</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {categories.map(c => (
          <button key={c.id} onClick={() => onSelect(c.id)}
            className="flex items-start gap-3 rounded-xl border p-4 text-left transition hover:shadow-md dark:border-gray-700">
            <span className="text-2xl">{c.icon}</span>
            <div>
              <p className="text-sm font-semibold">{c.name}</p>
              <p className="text-xs text-gray-400">{c.description}</p>
              <p className="mt-1 text-xs text-blue-600">{c.count} apps</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
