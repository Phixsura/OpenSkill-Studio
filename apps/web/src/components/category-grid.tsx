"use client";

interface Category { id: string; name: string; icon: string; count: number; color: string; }
interface CategoryGridProps { categories: Category[]; totalApps: number;
  onCategoryClick: (id: string) => void; }

const colorMap: Record<string, string> = {
  blue: "border-blue-200 hover:bg-blue-50 dark:border-blue-800 dark:hover:bg-blue-900/10",
  purple: "border-purple-200 hover:bg-purple-50 dark:border-purple-800 dark:hover:bg-purple-900/10",
  red: "border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/10",
  green: "border-green-200 hover:bg-green-50 dark:border-green-800 dark:hover:bg-green-900/10",
  pink: "border-pink-200 hover:bg-pink-50 dark:border-pink-800 dark:hover:bg-pink-900/10",
  yellow: "border-yellow-200 hover:bg-yellow-50 dark:border-yellow-800 dark:hover:bg-yellow-900/10",
  orange: "border-orange-200 hover:bg-orange-50 dark:border-orange-800 dark:hover:bg-orange-900/10",
  cyan: "border-cyan-200 hover:bg-cyan-50 dark:border-cyan-800 dark:hover:bg-cyan-900/10",
  emerald: "border-emerald-200 hover:bg-emerald-50 dark:border-emerald-800 dark:hover:bg-emerald-900/10",
  indigo: "border-indigo-200 hover:bg-indigo-50 dark:border-indigo-800 dark:hover:bg-indigo-900/10",
  violet: "border-violet-200 hover:bg-violet-50 dark:border-violet-800 dark:hover:bg-violet-900/10",
  amber: "border-amber-200 hover:bg-amber-50 dark:border-amber-800 dark:hover:bg-amber-900/10",
};

export function CategoryGrid({ categories, totalApps, onCategoryClick }: CategoryGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Browse Categories</h2>
        <span className="text-xs text-gray-400">{totalApps.toLocaleString()} apps across {categories.length} categories</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {categories.map(cat => (
          <button key={cat.id} onClick={() => onCategoryClick(cat.id)}
            className={`rounded-xl border p-4 text-left transition-colors ${colorMap[cat.color] ?? ""}`}>
            <span className="text-3xl">{cat.icon}</span>
            <h3 className="mt-2 font-semibold">{cat.name}</h3>
            <p className="text-xs text-gray-400">{cat.count} apps</p>
          </button>
        ))}
      </div>
    </div>
  );
}
