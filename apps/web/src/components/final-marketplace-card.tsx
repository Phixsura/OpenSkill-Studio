"use client";

interface FinalMarketplaceCardProps { name: string; icon: string; tagline: string;
  developer: string; stars: string; installsDisplay: string; priceDisplay: string;
  verified: boolean; category: string; badges: string[];
  onInstall: () => void; onClick: () => void; }

export function FinalMarketplaceCard({ name, icon, tagline, developer, stars,
  installsDisplay, priceDisplay, verified, category, badges, onInstall, onClick }: FinalMarketplaceCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4 hover:shadow-xl transition cursor-pointer" onClick={onClick}>
      <div className="flex items-start gap-3 mb-3">
        <span className="text-3xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <h4 className="text-sm font-bold truncate">{name}</h4>
            {verified && <span className="text-blue-500 text-xs shrink-0">✓</span>}
          </div>
          <p className="text-xs text-gray-400">{developer}</p>
          <p className="text-xs text-gray-500 truncate">{tagline}</p>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 shrink-0">{priceDisplay}</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex gap-2 text-xs text-gray-400">
          <span className="text-yellow-500">{stars}</span>
          <span>📥 {installsDisplay}</span>
          <span className="capitalize">{category}</span>
        </div>
        <button onClick={e => { e.stopPropagation(); onInstall(); }}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Install</button>
      </div>
      {badges.length > 0 && (
        <div className="flex gap-1 mt-2">
          {badges.map(b => <span key={b} className="text-xs px-1.5 py-0.5 rounded-full bg-yellow-100 text-yellow-700 capitalize">{b.replace("_", " ")}</span>)}
        </div>
      )}
    </div>
  );
}
