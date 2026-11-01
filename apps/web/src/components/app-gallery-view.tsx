"use client";

interface GalleryApp { name: string; slug: string; category: string; installCount: number; }
interface AppGalleryViewProps { title: string; apps: GalleryApp[]; sortBy: string; onSortChange?: (sort: string) => void; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊" };

export function AppGalleryView({ title, apps, sortBy, onSortChange }: AppGalleryViewProps) {
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold">{title}</h2>
        {onSortChange && (
          <select value={sortBy} onChange={e => onSortChange(e.target.value)} className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800">
            <option value="installs">Most Installed</option>
            <option value="newest">Newest</option>
            <option value="rating">Highest Rated</option>
            <option value="name">A-Z</option>
          </select>
        )}
      </div>
      {apps.length === 0 ? <p className="py-8 text-center text-gray-400">No apps found</p> : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {apps.map(a => (
            <a key={a.slug} href={`/marketplace/apps/${a.slug}`} className="rounded-lg border border-gray-200 p-3 hover:border-blue-400 dark:border-gray-700">
              <span className="mr-1">{ICONS[a.category] ?? "📦"}</span>
              <span className="font-medium">{a.name}</span>
              <span className="ml-2 text-xs text-gray-400">📥 {a.installCount}</span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
