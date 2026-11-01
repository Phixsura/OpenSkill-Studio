"use client";

import { useState } from "react";

interface AppResult {
  app_id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  publisher: string;
  rating: number;
  downloads: number;
  price_tier: "free" | "paid" | "freemium";
  tags: string[];
}

interface SearchResponse {
  results: { app: AppResult; score: number; highlights: string[] }[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
  facets: { category: Record<string, number>; price_tier: Record<string, number> };
}

interface MarketplaceSearchProps {
  response: SearchResponse;
  query: string;
  onQueryChange: (q: string) => void;
  onSearch: () => void;
  onCategoryFilter: (cat: string | null) => void;
  onInstall: (appId: string) => void;
  onLoadMore: () => void;
  activeCategory: string | null;
}

const TIER_BADGES: Record<string, { label: string; color: string }> = {
  free: {
    label: "Free",
    color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  },
  paid: {
    label: "Paid",
    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  },
  freemium: {
    label: "Freemium",
    color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
  },
};

function StarRating({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  return (
    <span className="text-xs text-yellow-500" aria-label={`${rating} stars`}>
      {"★".repeat(full)}
      {half ? "½" : ""}
      {"☆".repeat(5 - full - (half ? 1 : 0))}
      <span className="ml-1 text-gray-500">{rating.toFixed(1)}</span>
    </span>
  );
}

function AppCard({
  app,
  highlights,
  onInstall,
}: {
  app: AppResult;
  highlights: string[];
  onInstall: (id: string) => void;
}) {
  const tier = TIER_BADGES[app.price_tier] ?? TIER_BADGES.free;

  return (
    <div className="flex gap-3 rounded-lg border border-gray-200 p-3 hover:border-blue-300 dark:border-gray-700 dark:hover:border-blue-600">
      <span className="text-3xl">{app.icon}</span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h4 className="truncate text-sm font-semibold">{app.name}</h4>
          <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${tier.color}`}>
            {tier.label}
          </span>
        </div>
        <p className="mt-0.5 line-clamp-2 text-xs text-gray-500">{app.description}</p>
        <div className="mt-1.5 flex items-center gap-3">
          <StarRating rating={app.rating} />
          <span className="text-xs text-gray-400">{app.downloads.toLocaleString()} downloads</span>
          <span className="text-xs text-gray-400">by {app.publisher}</span>
        </div>
        {app.tags.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1">
            {app.tags.slice(0, 4).map((t) => (
              <span
                key={t}
                className={`rounded px-1.5 py-0.5 text-[10px] ${highlights.includes(t) ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}
              >
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
      <button
        onClick={() => onInstall(app.app_id)}
        className="shrink-0 self-center rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
      >
        Install
      </button>
    </div>
  );
}

export function MarketplaceSearch({
  response,
  query,
  onQueryChange,
  onSearch,
  onCategoryFilter,
  onInstall,
  onLoadMore,
  activeCategory,
}: MarketplaceSearchProps) {
  const categories = Object.entries(response.facets.category || {});

  return (
    <div className="space-y-4">
      {/* Search bar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSearch()}
          placeholder="Search apps, connectors, tools…"
          className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800"
          aria-label="Search marketplace"
        />
        <button
          onClick={onSearch}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {/* Category filters */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => onCategoryFilter(null)}
            className={`rounded-full px-2.5 py-1 text-xs ${!activeCategory ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"}`}
          >
            All
          </button>
          {categories.map(([cat, count]) => (
            <button
              key={cat}
              onClick={() => onCategoryFilter(cat)}
              className={`rounded-full px-2.5 py-1 text-xs ${activeCategory === cat ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"}`}
            >
              {cat} ({count})
            </button>
          ))}
        </div>
      )}

      {/* Results count */}
      <p className="text-xs text-gray-500">{response.total} results found</p>

      {/* Results */}
      {response.results.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">🔍</span>
          <p className="mt-2 text-sm text-gray-500">No apps found matching your search</p>
        </div>
      ) : (
        <div className="space-y-2">
          {response.results.map((r) => (
            <AppCard
              key={r.app.app_id}
              app={r.app}
              highlights={r.highlights}
              onInstall={onInstall}
            />
          ))}
        </div>
      )}

      {/* Load more */}
      {response.has_more && (
        <button
          onClick={onLoadMore}
          className="w-full rounded-lg border border-gray-300 py-2 text-sm text-gray-600 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          Load more
        </button>
      )}
    </div>
  );
}
