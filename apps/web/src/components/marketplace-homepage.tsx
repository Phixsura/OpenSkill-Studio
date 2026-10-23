"use client";

interface App { id: string; name: string; }
interface Category { id: string; name: string; count: number; }
interface Stats { total_apps: number; total_developers: number; total_installs: number; avg_rating: number; }
interface Announcement { title: string; body: string; }
interface MarketplaceHomepageProps { hero: { title: string; subtitle: string; cta: string; app_count: number; developer_count: number };
  featuredApps: App[]; trendingApps: App[]; categories: Category[]; stats: Stats;
  announcements: Announcement[]; onSearch: (query: string) => void; onAppClick: (id: string) => void; }

export function MarketplaceHomepage({ hero, featuredApps, trendingApps, categories, stats, announcements, onSearch, onAppClick }: MarketplaceHomepageProps) {
  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 p-10 text-center text-white">
        <h1 className="text-4xl font-black">{hero.title}</h1>
        <p className="mt-2 text-lg opacity-80">{hero.subtitle}</p>
        <div className="mt-4 flex justify-center gap-4 text-sm opacity-70">
          <span>📦 {hero.app_count.toLocaleString()} apps</span>
          <span>👨‍💻 {hero.developer_count.toLocaleString()} developers</span>
        </div>
        <div className="mx-auto mt-6 max-w-md">
          <input placeholder="Search apps..." onKeyDown={e => e.key === "Enter" && onSearch((e.target as HTMLInputElement).value)}
            className="w-full rounded-full bg-white/20 px-6 py-3 text-white placeholder-white/50 backdrop-blur" />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Apps", value: stats.total_apps.toLocaleString(), icon: "📦" },
          { label: "Developers", value: stats.total_developers.toLocaleString(), icon: "👨‍💻" },
          { label: "Installs", value: stats.total_installs.toLocaleString(), icon: "📥" },
          { label: "Avg Rating", value: `⭐ ${stats.avg_rating}`, icon: "" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border p-4 text-center dark:border-gray-700">
            <p className="text-2xl font-bold">{s.icon} {s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Featured */}
      <div>
        <h2 className="text-xl font-bold">⭐ Featured Apps</h2>
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {featuredApps.map(app => (
            <button key={app.id} onClick={() => onAppClick(app.id)}
              className="rounded-lg border p-4 text-left hover:border-blue-400 dark:border-gray-700">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 text-lg text-white">
                {app.name.charAt(0)}
              </div>
              <p className="mt-2 font-medium">{app.name}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Trending */}
      <div>
        <h2 className="text-xl font-bold">🔥 Trending Now</h2>
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {trendingApps.map(app => (
            <button key={app.id} onClick={() => onAppClick(app.id)}
              className="rounded-lg border p-3 text-left dark:border-gray-700">
              <p className="font-medium">{app.name}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div>
          <h2 className="text-xl font-bold">📂 Categories</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {categories.map(cat => (
              <span key={cat.id} className="rounded-full border px-4 py-1.5 text-sm dark:border-gray-600">
                {cat.name} <span className="text-xs text-gray-400">({cat.count})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Announcements */}
      {announcements.length > 0 && (
        <div>
          <h2 className="text-xl font-bold">📢 Announcements</h2>
          <div className="mt-3 space-y-2">
            {announcements.map((a, i) => (
              <div key={i} className="rounded-lg border p-3 dark:border-gray-700">
                <p className="font-medium">{a.title}</p>
                <p className="text-sm text-gray-400">{a.body}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
