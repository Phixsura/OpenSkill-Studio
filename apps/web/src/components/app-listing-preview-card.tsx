"use client";

interface ListingCard { name: string; tagline: string; developer: string; rating: number;
  stars: string; install_count: string; price_label: string; category: string; }
interface Completeness { pct: number; completed: number; total: number; }
interface AppListingPreviewCardProps { card: ListingCard; completeness: Completeness; }

export function AppListingPreviewCard({ card, completeness }: AppListingPreviewCardProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Listing Preview</h2>
      <div className="rounded-lg border p-4 shadow dark:border-gray-700">
        <div className="flex gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 text-2xl text-white">
            {card.name.charAt(0)}
          </div>
          <div className="flex-1">
            <h3 className="font-bold">{card.name}</h3>
            <p className="text-xs text-gray-400">{card.developer}</p>
            <p className="mt-1 text-xs text-gray-500">{card.tagline}</p>
          </div>
          <div className="text-right">
            <p className="font-bold text-blue-600">{card.price_label}</p>
            <p className="text-xs text-yellow-500">{card.stars}</p>
            <p className="text-xs text-gray-400">{card.install_count}</p>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <span>Completeness:</span>
        <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${completeness.pct === 100 ? "bg-green-500" : "bg-yellow-500"}`}
            style={{ width: `${completeness.pct}%` }} />
        </div>
        <span className="text-xs text-gray-400">{completeness.completed}/{completeness.total}</span>
      </div>
    </div>
  );
}
