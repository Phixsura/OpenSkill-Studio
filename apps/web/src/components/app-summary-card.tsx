"use client";

interface AppSummaryCardProps { name: string; icon: string; tagline: string; version: string;
  stars: string; installsDisplay: string; verified: boolean; category: string;
  author: string; onClick: () => void; }

export function AppSummaryCard({ name, icon, tagline, version, stars, installsDisplay,
  verified, category, author, onClick }: AppSummaryCardProps) {
  return (
    <button onClick={onClick}
      className="flex w-full items-start gap-3 rounded-xl border p-4 text-left transition hover:shadow-md dark:border-gray-700">
      <span className="text-3xl shrink-0">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <h3 className="text-sm font-bold truncate">{name}</h3>
          {verified && <span className="text-blue-500 text-xs">✓</span>}
          <span className="text-xs text-gray-400">v{version}</span>
        </div>
        <p className="text-xs text-gray-500 truncate mt-0.5">{tagline}</p>
        <div className="mt-1.5 flex items-center gap-3 text-xs text-gray-400">
          <span className="text-yellow-500">{stars}</span>
          <span>{installsDisplay} installs</span>
          <span className="capitalize">{category}</span>
          <span>by {author}</span>
        </div>
      </div>
    </button>
  );
}
