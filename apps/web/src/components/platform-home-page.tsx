"use client";

interface FeaturedApp { id: string; name: string; icon: string; tagline: string; rating: number; }
interface TrendingApp { id: string; name: string; icon: string; growth: number; }
interface Category { id: string; name: string; icon: string; count: number; }
interface PlatformStats { apps: number; developers: number; downloads: number; uptime: number; }
interface PlatformHomePageProps { heroTitle: string; heroSubtitle: string; stats: PlatformStats;
  featured: FeaturedApp[]; trending: TrendingApp[]; categories: Category[];
  onSelectApp: (id: string) => void; onSelectCategory: (id: string) => void; onSearch: (q: string) => void; }

export function PlatformHomePage({ heroTitle, heroSubtitle, stats, featured, trending,
  categories, onSelectApp, onSelectCategory, onSearch }: PlatformHomePageProps) {
  return (
    <div className="space-y-12">
      <section className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-12 text-center text-white">
        <h1 className="text-4xl font-extrabold">{heroTitle}</h1>
        <p className="mt-3 text-lg opacity-90">{heroSubtitle}</p>
        <div className="mx-auto mt-6 max-w-md">
          <input type="search" placeholder="🔍 Search apps..." onChange={e => onSearch(e.target.value)}
            className="w-full rounded-xl bg-white/20 px-5 py-3 text-sm text-white placeholder-white/70 backdrop-blur" />
        </div>
        <div className="mt-8 flex justify-center gap-8">
          <div><p className="text-3xl font-bold">{stats.apps.toLocaleString()}</p><p className="text-sm opacity-80">Apps</p></div>
          <div><p className="text-3xl font-bold">{stats.developers.toLocaleString()}</p><p className="text-sm opacity-80">Developers</p></div>
          <div><p className="text-3xl font-bold">{(stats.downloads / 1_000_000).toFixed(1)}M</p><p className="text-sm opacity-80">Downloads</p></div>
          <div><p className="text-3xl font-bold">{stats.uptime}%</p><p className="text-sm opacity-80">Uptime</p></div>
        </div>
      </section>
      {featured.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4">⭐ Featured</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {featured.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex items-center gap-3 rounded-xl border p-4 text-left hover:shadow dark:border-gray-700">
                <span className="text-3xl">{a.icon}</span>
                <div><p className="font-semibold">{a.name}</p><p className="text-xs text-gray-400">{a.tagline}</p>
                  <span className="text-xs text-yellow-500">⭐ {a.rating}</span></div>
              </button>
            ))}
          </div>
        </section>
      )}
      {trending.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4">🔥 Trending</h2>
          <div className="flex gap-3 overflow-x-auto">
            {trending.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex shrink-0 items-center gap-2 rounded-xl border px-4 py-3 dark:border-gray-700">
                <span className="text-2xl">{a.icon}</span>
                <div><p className="text-sm font-medium">{a.name}</p><p className="text-xs text-green-600">↑ {a.growth}%</p></div>
              </button>
            ))}
          </div>
        </section>
      )}
      {categories.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4">📂 Categories</h2>
          <div className="flex flex-wrap gap-2">
            {categories.map(c => (
              <button key={c.id} onClick={() => onSelectCategory(c.id)}
                className="flex items-center gap-1.5 rounded-full border px-4 py-2 text-sm hover:bg-gray-50 dark:border-gray-700">
                {c.icon} {c.name} <span className="text-xs text-gray-400">({c.count})</span>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
