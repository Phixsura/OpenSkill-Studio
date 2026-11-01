"use client";

interface AppStoreCardProps { name: string; shortDescription: string; icon: string;
  category: string; version: string; author: string; downloads: number;
  avgRating: number; starsDisplay: string; reviewCount: number;
  pricing: string; verified: boolean; tags: string[]; }

export function AppStoreCard({ name, shortDescription, icon, category, version,
  author, downloads, avgRating, starsDisplay, reviewCount, pricing, verified, tags }: AppStoreCardProps) {
  return (
    <div className="rounded-xl border p-5 hover:shadow-lg transition dark:border-gray-700">
      <div className="flex items-start gap-4">
        <span className="text-4xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold truncate">{name}</h3>
            {verified && <span className="text-blue-500" title="Verified">✓</span>}
          </div>
          <p className="text-sm text-gray-500 line-clamp-2">{shortDescription}</p>
          <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
            <span className="text-yellow-500">{starsDisplay}</span>
            <span>{avgRating} ({reviewCount})</span>
            <span>{downloads.toLocaleString()} downloads</span>
          </div>
          <div className="mt-2 flex items-center justify-between">
            <div className="flex gap-1">
              {tags.slice(0, 3).map(t => (
                <span key={t} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{t}</span>
              ))}
            </div>
            <span className="text-sm font-semibold text-blue-600">{pricing}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
