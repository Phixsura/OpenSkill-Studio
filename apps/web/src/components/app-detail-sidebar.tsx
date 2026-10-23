"use client";

interface AppDetailSidebarProps {
  installCount: number; activeCount: number; avgRating: number; reviewCount: number;
  screenshots: string[]; onInstall: () => void;
}

export function AppDetailSidebar({ installCount, activeCount, avgRating, reviewCount, screenshots, onInstall }: AppDetailSidebarProps) {
  return (
    <div className="space-y-4">
      <button onClick={onInstall}
        className="w-full rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white hover:bg-blue-700">
        Install App
      </button>
      <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
        <div className="grid grid-cols-2 gap-3 text-center">
          <div><p className="text-lg font-bold">{installCount.toLocaleString()}</p><p className="text-xs text-gray-400">Installs</p></div>
          <div><p className="text-lg font-bold">{activeCount.toLocaleString()}</p><p className="text-xs text-gray-400">Active</p></div>
          <div><p className="text-lg font-bold">{avgRating.toFixed(1)} ★</p><p className="text-xs text-gray-400">Rating</p></div>
          <div><p className="text-lg font-bold">{reviewCount}</p><p className="text-xs text-gray-400">Reviews</p></div>
        </div>
      </div>
      {screenshots.length > 0 && (
        <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-500">Screenshots</p>
          <div className="mt-2 grid grid-cols-2 gap-1">
            {screenshots.slice(0, 4).map((s, i) => (
              <div key={i} className="aspect-video rounded bg-gray-100 dark:bg-gray-700" />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
