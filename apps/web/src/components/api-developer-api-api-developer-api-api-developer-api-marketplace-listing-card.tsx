"use client";

interface ListingInfo { listing_id: string; app_name: string; description: string; category: string; pricing: string; status: string; installs: number; rating: number; }
interface Props { listings: ListingInfo[]; appName: string; }

const pBadge: Record<string, string> = { free: "bg-green-100 text-green-700", freemium: "bg-blue-100 text-blue-700", paid: "bg-purple-100 text-purple-700" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListingCard({ listings, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏪 Marketplace</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {listings.length} listings</p>
      </div>
      {listings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No marketplace listings</p>
      ) : (
        <div className="space-y-2">
          {listings.slice(0, 5).map((l) => (
            <div key={l.listing_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{l.app_name}</span>
                  <span className={`rounded px-1 py-0.5 text-[9px] ${pBadge[l.pricing] ?? ""}`}>{l.pricing}</span>
                </div>
                <span className="text-gray-400">{l.installs.toLocaleString()} installs</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400 truncate">{l.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
