"use client";

interface ListingInfo { listing_id: string; name: string; category: string; install_count: number; rating: number; published: boolean; }
interface Props { listings: ListingInfo[]; appName: string; }

export default function APIDeveloperMarketplaceCard({ listings, appName }: Props) {
  const published = listings.filter((l) => l.published).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏪 Marketplace</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{published}/{listings.length} published</span>
      </div>
      {listings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No marketplace listings</p>
      ) : (
        <div className="space-y-1.5">
          {listings.map((l) => (
            <div key={l.listing_id} className={`flex items-center justify-between text-[11px] ${!l.published ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="text-gray-700 dark:text-gray-300">{l.name}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{l.category}</span>
              </div>
              <span className="text-gray-400">{l.install_count} installs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
