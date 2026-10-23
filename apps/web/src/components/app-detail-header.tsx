"use client";

interface AppDetailHeaderProps { name: string; developer: string; tagline: string;
  iconLetter: string; rating: number; stars: string; reviewCount: number;
  installDisplay: string; priceLabel: string; category: string; verified: boolean;
  version: string; onInstall: () => void; }

export function AppDetailHeader({ name, developer, tagline, iconLetter, rating, stars,
  reviewCount, installDisplay, priceLabel, category, verified, version, onInstall }: AppDetailHeaderProps) {
  return (
    <div className="flex gap-5">
      <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-3xl font-bold text-white">
        {iconLetter}
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-black">{name}</h1>
          {verified && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">✓ Verified</span>}
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">v{version}</span>
        </div>
        <p className="mt-0.5 text-sm text-gray-400">by {developer}</p>
        <p className="mt-1 text-sm text-gray-500">{tagline}</p>
        <div className="mt-2 flex items-center gap-4 text-sm">
          <span className="text-yellow-500">{stars} <span className="text-gray-400">({reviewCount})</span></span>
          <span className="text-gray-400">📥 {installDisplay}</span>
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{category}</span>
        </div>
      </div>
      <div className="flex flex-col items-end gap-2">
        <button onClick={onInstall}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white">
          {priceLabel === "Free" ? "Install Free" : `Install — ${priceLabel}`}
        </button>
      </div>
    </div>
  );
}
