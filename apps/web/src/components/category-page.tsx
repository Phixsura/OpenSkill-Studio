"use client";

interface CategoryInfo { id: string; name: string; icon: string; description: string; }
interface CategoryApp { id: string; name: string; icon: string; tagline: string; rating: number; downloads: number; }
interface CategoryPageProps { category: CategoryInfo; apps: CategoryApp[]; total: number;
  sortBy: string; onSort: (sort: string) => void; onSelectApp: (id: string) => void; }

export function CategoryPage({ category, apps, total, sortBy, onSort, onSelectApp }: CategoryPageProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{category.icon}</span>
        <div>
          <h1 className="text-2xl font-bold">{category.name}</h1>
          <p className="text-sm text-gray-500">{category.description}</p>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{total} apps</span>
        <select value={sortBy} onChange={e => onSort(e.target.value)}
          className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
          <option value="popular">Most Popular</option>
          <option value="rating">Top Rated</option>
          <option value="newest">Newest</option>
        </select>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {apps.map(a => (
          <button key={a.id} onClick={() => onSelectApp(a.id)}
            className="flex items-center gap-3 rounded-xl border p-4 text-left hover:shadow dark:border-gray-700">
            <span className="text-2xl">{a.icon}</span>
            <div className="flex-1 min-w-0">
              <p className="font-semibold">{a.name}</p>
              <p className="text-xs text-gray-400 truncate">{a.tagline}</p>
              <div className="mt-1 flex gap-2 text-xs text-gray-400">
                <span>⭐ {a.rating}</span>
                <span>📥 {a.downloads.toLocaleString()}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
