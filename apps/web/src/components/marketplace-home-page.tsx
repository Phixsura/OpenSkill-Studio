"use client";

interface App { id: string; name: string; icon: string; }
interface FeaturedApp extends App { tagline: string; rating: number; }
interface TrendingApp extends App { growthPct: number; }
interface Category { id: string; name: string; icon: string; count: number; }
interface MarketplaceHomePageProps {
  heroTitle: string; heroSubtitle: string; appsDisplay: string; devsDisplay: string;
  featured: FeaturedApp[]; trending: TrendingApp[]; categories: Category[];
  newApps: App[]; onSelectApp: (id: string) => void; onSelectCategory: (id: string) => void;
}

export function MarketplaceHomePage({ heroTitle, heroSubtitle, appsDisplay, devsDisplay,
  featured, trending, categories, newApps, onSelectApp, onSelectCategory }: MarketplaceHomePageProps) {
  return (
    <div className="space-y-10">
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-10 text-center text-white">
        <h1 className="text-3xl font-extrabold sm:text-4xl">{heroTitle}</h1>
        <p className="mt-3 text-lg opacity-90">{heroSubtitle}</p>
        <div className="mt-6 flex justify-center gap-8">
          <div><p className="text-3xl font-bold">{appsDisplay}</p><p className="text-sm opacity-80">Apps</p></div>
          <div><p className="text-3xl font-bold">{devsDisplay}</p><p className="text-sm opacity-80">Developers</p></div>
        </div>
      </div>
      <section>
        <h2 className="text-lg font-bold mb-3">⭐ Featured</h2>
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
      <section>
        <h2 className="text-lg font-bold mb-3">🔥 Trending</h2>
        <div className="flex gap-3 overflow-x-auto">
          {trending.map(a => (
            <button key={a.id} onClick={() => onSelectApp(a.id)}
              className="flex shrink-0 items-center gap-2 rounded-xl border px-4 py-3 dark:border-gray-700">
              <span className="text-2xl">{a.icon}</span>
              <div><p className="text-sm font-medium">{a.name}</p>
                <p className="text-xs text-green-600">↑ {a.growthPct}%</p></div>
            </button>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">📂 Categories</h2>
        <div className="flex flex-wrap gap-2">
          {categories.map(c => (
            <button key={c.id} onClick={() => onSelectCategory(c.id)}
              className="flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm hover:bg-gray-50 dark:border-gray-700">
              {c.icon} {c.name} <span className="text-xs text-gray-400">({c.count})</span>
            </button>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">🆕 New Apps</h2>
        <div className="grid grid-cols-4 gap-2">
          {newApps.map(a => (
            <button key={a.id} onClick={() => onSelectApp(a.id)}
              className="flex flex-col items-center gap-1 rounded-xl border p-3 dark:border-gray-700">
              <span className="text-2xl">{a.icon}</span>
              <span className="text-xs truncate w-full text-center">{a.name}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
