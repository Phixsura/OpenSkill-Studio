"use client";

interface AppDetailHeroProps { name: string; tagline: string; icon: string;
  developer: string; verified: boolean; stars: string; reviewCount: number;
  installsDisplay: string; priceDisplay: string; version: string;
  category: string; tags: string[];
  onInstall: () => void; }

export function AppDetailHero({ name, tagline, icon, developer, verified, stars,
  reviewCount, installsDisplay, priceDisplay, version, category, tags, onInstall }: AppDetailHeroProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-6">
      <div className="flex items-start gap-4 mb-4">
        <span className="text-5xl">{icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">{name}</h1>
            {verified && <span className="text-blue-500 text-sm">✓ Verified</span>}
          </div>
          <p className="text-sm text-gray-500 mb-1">{tagline}</p>
          <p className="text-xs text-gray-400">By {developer} · {category} · v{version}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold mb-1">{priceDisplay}</p>
          <button onClick={onInstall}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Install</button>
        </div>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-yellow-500">{stars}</span>
        <span className="text-gray-400">{reviewCount} reviews</span>
        <span className="text-gray-400">📥 {installsDisplay}</span>
      </div>
      {tags.length > 0 && (
        <div className="flex gap-1 mt-3">
          {tags.map(t => <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800">{t}</span>)}
        </div>
      )}
    </div>
  );
}
