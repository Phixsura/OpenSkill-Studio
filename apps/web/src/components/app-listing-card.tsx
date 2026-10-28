"use client";

interface ListingInfo {
  listing_id: string;
  name: string;
  description: string;
  category: string;
  status: "draft" | "published" | "unlisted";
  install_count: number;
  avg_rating: number;
  rating_count: number;
  tags: string[];
}

interface AppListingCardProps {
  listings: ListingInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  draft: { bg: "bg-gray-100 dark:bg-gray-800", text: "text-gray-600 dark:text-gray-400" },
  published: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
  },
  unlisted: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
};

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function AppListingCard({ listings, appName }: AppListingCardProps) {
  const publishedCount = listings.filter((l) => l.status === "published").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">App Listings</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{publishedCount} published</span>
      </div>

      {listings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No listings</p>
      ) : (
        <div className="space-y-2">
          {listings.map((l) => {
            const st = STATUS_STYLES[l.status] ?? STATUS_STYLES.draft;
            return (
              <div
                key={l.listing_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {l.name}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}
                    >
                      {l.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-gray-400">
                    {l.avg_rating > 0 && <span>⭐ {l.avg_rating}</span>}
                    <span>{formatNum(l.install_count)} installs</span>
                  </div>
                </div>
                <p className="mt-0.5 truncate text-xs text-gray-500">{l.description}</p>
                {l.tags.length > 0 && (
                  <div className="mt-1 flex gap-1">
                    {l.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
