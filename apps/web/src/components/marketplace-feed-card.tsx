"use client";

interface FeedEntry { title: string; link: string; published: string; author: string; summary: string; }
interface MarketplaceFeedCardProps { entries: FeedEntry[]; }

export function MarketplaceFeedCard({ entries }: MarketplaceFeedCardProps) {
  if (entries.length === 0) return <p className="text-sm text-gray-400">No recent updates.</p>;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Marketplace Updates</h3>
      <ul className="mt-3 space-y-3">
        {entries.slice(0, 10).map((e, i) => (
          <li key={i} className="border-b pb-2 last:border-0 dark:border-gray-700">
            <a href={e.link} className="text-sm font-medium text-blue-600 hover:underline">{e.title}</a>
            <p className="text-xs text-gray-500">{e.summary}</p>
            <p className="mt-0.5 text-xs text-gray-400">{e.author} · {e.published.slice(0, 10)}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
