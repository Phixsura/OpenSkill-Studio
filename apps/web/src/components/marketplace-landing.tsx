"use client";

interface FeaturedApp { id: string; name: string; icon: string; tagline: string; }
interface Category { id: string; name: string; icon: string; appCount: number; }
interface MarketplaceLandingProps { featured: FeaturedApp[]; categories: Category[];
  stats: { totalApps: number; totalDevelopers: number; totalDownloads: number };
  onSelectApp: (id: string) => void; onSelectCategory: (id: string) => void; }

export function MarketplaceLanding({ featured, categories, stats, onSelectApp, onSelectCategory }: MarketplaceLandingProps) {
  return (
    <div className="space-y-10">
      <div className="text-center py-12">
        <h1 className="text-4xl font-extrabold">Discover apps for your workflow</h1>
        <p className="mt-3 text-lg text-gray-500">Browse thousands of integrations, tools, and extensions</p>
        <div className="mt-6 flex justify-center gap-8">
          <div><span className="text-2xl font-bold">{stats.totalApps.toLocaleString()}</span><p className="text-xs text-gray-400">Apps</p></div>
          <div><span className="text-2xl font-bold">{stats.totalDevelopers.toLocaleString()}</span><p className="text-xs text-gray-400">Developers</p></div>
          <div><span className="text-2xl font-bold">{stats.totalDownloads.toLocaleString()}</span><p className="text-xs text-gray-400">Downloads</p></div>
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">⭐ Featured</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {featured.map(a => (
            <button key={a.id} onClick={() => onSelectApp(a.id)}
              className="flex items-center gap-3 rounded-xl border p-4 text-left hover:shadow dark:border-gray-700">
              <span className="text-3xl">{a.icon}</span>
              <div><p className="font-semibold">{a.name}</p><p className="text-xs text-gray-400">{a.tagline}</p></div>
            </button>
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">📂 Categories</h2>
        <div className="flex flex-wrap gap-2">
          {categories.map(c => (
            <button key={c.id} onClick={() => onSelectCategory(c.id)}
              className="flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
              <span>{c.icon}</span>{c.name}<span className="text-xs text-gray-400">({c.appCount})</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
