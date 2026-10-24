"use client";

interface AppPreview { name: string; icon: string; rating: number; category: string; }
interface CategoryPreview { id: string; label: string; icon: string; count: number; }
interface MarketplaceHomePageProps {
  heroTitle: string; heroSubtitle: string; heroCta: string;
  featured: AppPreview[]; categories: CategoryPreview[];
  trending: AppPreview[]; newApps: AppPreview[];
  appsDisplay: string; devsDisplay: string;
  onSearch: (q: string) => void; onCategory: (id: string) => void; }

export function MarketplaceHomePage({ heroTitle, heroSubtitle, heroCta,
  featured, categories, trending, newApps, appsDisplay, devsDisplay,
  onSearch, onCategory }: MarketplaceHomePageProps) {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white text-center">
        <h1 className="text-3xl font-bold mb-2">{heroTitle}</h1>
        <p className="text-lg opacity-90 mb-4">{heroSubtitle}</p>
        <div className="max-w-md mx-auto">
          <input placeholder="Search apps..." onChange={e => onSearch(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg text-gray-900 text-sm" />
        </div>
      </div>
      <div>
        <h2 className="font-semibold mb-3">📦 Categories</h2>
        <div className="flex gap-2 overflow-x-auto">
          {categories.map(c => (
            <button key={c.id} onClick={() => onCategory(c.id)}
              className="shrink-0 px-4 py-2 rounded-lg border dark:border-gray-700 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
              {c.icon} {c.label} <span className="text-xs text-gray-400">({c.count})</span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <h2 className="font-semibold mb-3">⭐ Featured</h2>
        <div className="grid grid-cols-3 gap-3">
          {featured.map(a => (
            <div key={a.name} className="rounded-lg border dark:border-gray-700 p-3 text-center">
              <span className="text-3xl">{a.icon}</span>
              <p className="text-sm font-medium mt-1">{a.name}</p>
              <p className="text-xs text-gray-400">⭐ {a.rating}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-4 justify-center text-sm text-gray-400">
        <span>📱 {appsDisplay} apps</span>
        <span>👩‍💻 {devsDisplay} developers</span>
      </div>
    </div>
  );
}
