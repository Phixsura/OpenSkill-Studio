"use client";

interface AppHeader { name: string; icon: string; tagline: string; author: string;
  verified: boolean; version: string; }
interface AppStats { downloads: number; rating: number; stars: string; reviewCount: number; }
interface AppOverviewPageProps { header: AppHeader; stats: AppStats; description: string;
  pricing: string; tags: string[]; installCta: string; onInstall: () => void; }

export function AppOverviewPage({ header, stats, description, pricing, tags, installCta, onInstall }: AppOverviewPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-start gap-4">
        <span className="text-5xl">{header.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold">{header.name}</h1>
            {header.verified && <span className="text-blue-500">✓</span>}
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">v{header.version}</span>
          </div>
          <p className="mt-1 text-gray-500">{header.tagline}</p>
          <p className="text-xs text-gray-400">by {header.author}</p>
          <div className="mt-2 flex items-center gap-3">
            <span className="text-yellow-500 text-sm">{stats.stars}</span>
            <span className="text-xs text-gray-400">{stats.rating} ({stats.reviewCount} reviews)</span>
            <span className="text-xs text-gray-400">{stats.downloads.toLocaleString()} downloads</span>
          </div>
        </div>
        <button onClick={onInstall} className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white">{installCta}</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tags.map(t => <span key={t} className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-700">{t}</span>)}
      </div>
      <div className="prose dark:prose-invert text-sm"><p>{description}</p></div>
    </div>
  );
}
