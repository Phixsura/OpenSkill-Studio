"use client";

interface Badge { type: string; label: string; icon: string; }
interface AppCardV2Props {
  name: string; description: string; category: string; developerName: string;
  rating: number; reviewCount: number; installCount: number;
  badges: Badge[]; price: string; slug: string;
}

export function AppCardV2({ name, description, category, developerName, rating, reviewCount, installCount, badges, price, slug }: AppCardV2Props) {
  return (
    <a href={`/marketplace/apps/${slug}`}
      className="block rounded-lg border border-gray-200 p-4 transition hover:shadow-md dark:border-gray-700">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold">{name}</h3>
          <p className="text-xs text-gray-400">{developerName} · {category}</p>
        </div>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{price}</span>
      </div>
      <p className="mt-2 text-sm text-gray-500 line-clamp-2">{description}</p>
      <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
        <span className="text-yellow-400">{"★".repeat(Math.round(rating))}{"☆".repeat(5 - Math.round(rating))}</span>
        <span>{reviewCount} reviews</span>
        <span>{installCount.toLocaleString()} installs</span>
      </div>
      {badges.length > 0 && (
        <div className="mt-2 flex gap-1">
          {badges.map(b => <span key={b.type} className="rounded bg-blue-50 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/20">{b.icon} {b.label}</span>)}
        </div>
      )}
    </a>
  );
}
