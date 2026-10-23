"use client";

interface MarketplaceAppCardProps { name: string; description: string; icon: string;
  category: string; stars: string; installDisplay: string; verified: boolean;
  priceDisplay: string; developer: string; onInstall: () => void; }

export function MarketplaceAppCard({ name, description, icon, category, stars,
  installDisplay, verified, priceDisplay, developer, onInstall }: MarketplaceAppCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4 hover:shadow-lg transition">
      <div className="flex items-start gap-3 mb-3">
        <span className="text-3xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <h4 className="text-sm font-bold truncate">{name}</h4>
            {verified && <span className="text-blue-500 text-xs" title="Verified">✓</span>}
          </div>
          <p className="text-xs text-gray-400">{developer}</p>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{priceDisplay}</span>
      </div>
      <p className="text-xs text-gray-500 mb-3 line-clamp-2">{description}</p>
      <div className="flex items-center justify-between">
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{stars}</span>
          <span>📥 {installDisplay}</span>
          <span className="capitalize">{category}</span>
        </div>
        <button onClick={onInstall}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Install</button>
      </div>
    </div>
  );
}
