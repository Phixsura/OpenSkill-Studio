"use client";

interface FeaturedApp { id: string; name?: string; featured_reason?: string; }
interface FeaturedAppsSectionProps { hero: FeaturedApp | null; grid: FeaturedApp[]; rest: FeaturedApp[]; title: string; }

export function FeaturedAppsSection({ hero, grid, rest, title }: FeaturedAppsSectionProps) {
  return (
    <div>
      <h2 className="text-xl font-bold">{title}</h2>
      {hero && (
        <div className="mt-4 rounded-xl border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50 p-6 dark:border-blue-800 dark:from-blue-900/20 dark:to-purple-900/20">
          <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">⭐ Featured</span>
          <h3 className="mt-2 text-lg font-bold">{hero.name || hero.id}</h3>
        </div>
      )}
      {grid.length > 0 && (
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {grid.map(a => (
            <div key={a.id} className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
              <p className="text-sm font-semibold">{a.name || a.id}</p>
              {a.featured_reason === "trending" && <span className="text-xs text-orange-500">🔥 Trending</span>}
            </div>
          ))}
        </div>
      )}
      {rest.length > 0 && (
        <ul className="mt-3 space-y-1">
          {rest.map(a => <li key={a.id} className="text-sm text-gray-600 dark:text-gray-400">• {a.name || a.id}</li>)}
        </ul>
      )}
    </div>
  );
}
