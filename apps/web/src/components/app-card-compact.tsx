"use client";

interface AppCardCompactProps { id: string; name: string; developer: string; iconLetter: string;
  rating: number; starsDisplay: string; installDisplay: string; priceLabel: string;
  category: string; onClick: (id: string) => void; }

export function AppCardCompact({ id, name, developer, iconLetter, rating, starsDisplay,
  installDisplay, priceLabel, category, onClick }: AppCardCompactProps) {
  return (
    <button onClick={() => onClick(id)}
      className="flex w-full items-center gap-3 rounded-lg border p-3 text-left hover:border-blue-400 hover:shadow dark:border-gray-700">
      <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 text-lg font-bold text-white">
        {iconLetter}
      </div>
      <div className="flex-1 min-w-0">
        <p className="truncate font-semibold">{name}</p>
        <p className="text-xs text-gray-400">{developer}</p>
        <div className="mt-0.5 flex items-center gap-2 text-xs">
          <span className="text-yellow-500">{starsDisplay}</span>
          <span className="text-gray-400">{installDisplay}</span>
          {category && <span className="rounded bg-gray-100 px-1 py-0.5 text-[10px] dark:bg-gray-800">{category}</span>}
        </div>
      </div>
      <span className="flex-shrink-0 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700 dark:bg-blue-900/20">
        {priceLabel}
      </span>
    </button>
  );
}
