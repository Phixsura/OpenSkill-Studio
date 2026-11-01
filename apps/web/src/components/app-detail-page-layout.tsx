"use client";

interface Header { name: string; developer: string; tagline: string; rating: number;
  install_count: number; price: number; version: string; }
interface Review { rating: number; text: string; }
interface RelatedApp { id: string; name: string; }
interface AppDetailPageLayoutProps { header: Header; description: string;
  reviews: { total: number; avg_rating: number; recent: Review[] };
  relatedApps: RelatedApp[]; permissions: string[]; tabs: string[];
  onInstall: () => void; onTabChange: (tab: string) => void; onRelatedClick: (id: string) => void; }

export function AppDetailPageLayout({ header, description, reviews, relatedApps,
  permissions, tabs, onInstall, onTabChange, onRelatedClick }: AppDetailPageLayoutProps) {
  const priceLabel = header.price === 0 ? "Free" : `$${header.price}/mo`;
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex gap-5">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-2xl font-bold text-white">
          {header.name.charAt(0)}
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-black">{header.name}</h1>
          <p className="text-sm text-gray-400">by {header.developer} · v{header.version}</p>
          <p className="mt-1 text-sm text-gray-500">{header.tagline}</p>
        </div>
        <button onClick={onInstall} className="self-start rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white">
          {priceLabel === "Free" ? "Install Free" : `Install — ${priceLabel}`}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b dark:border-gray-700">
        {tabs.map(tab => (
          <button key={tab} onClick={() => onTabChange(tab)} className="border-b-2 border-transparent px-1 pb-2 text-sm hover:border-blue-500">
            {tab}
          </button>
        ))}
      </div>

      {/* Description */}
      <div>
        <h2 className="text-lg font-semibold">About</h2>
        <p className="mt-2 text-sm text-gray-500">{description}</p>
      </div>

      {/* Reviews */}
      <div>
        <h2 className="text-lg font-semibold">Reviews ({reviews.total})</h2>
        <p className="text-sm text-gray-400">Average: ⭐ {reviews.avg_rating}</p>
      </div>

      {/* Related */}
      {relatedApps.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold">Related Apps</h2>
          <div className="mt-2 flex gap-2">
            {relatedApps.map(a => (
              <button key={a.id} onClick={() => onRelatedClick(a.id)}
                className="rounded-lg border px-3 py-2 text-sm dark:border-gray-700">{a.name}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
