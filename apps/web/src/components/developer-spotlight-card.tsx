"use client";

interface TopApp { name: string; slug: string; }
interface DeveloperSpotlightCardProps {
  name: string; slug: string; bio: string; verified: boolean; avatarInitial: string;
  stats: { apps: number; installs: number; rating: number }; topApps: TopApp[];
}

export function DeveloperSpotlightCard({ name, slug, bio, verified, avatarInitial, stats, topApps }: DeveloperSpotlightCardProps) {
  return (
    <a href={`/marketplace/developers/${slug}`}
      className="block rounded-xl border border-gray-200 p-5 transition hover:shadow-lg dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-lg font-bold text-white">
          {avatarInitial}
        </div>
        <div>
          <h3 className="font-semibold">{name} {verified && <span className="text-blue-600">✅</span>}</h3>
          <p className="text-xs text-gray-500 line-clamp-1">{bio}</p>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div><p className="font-bold">{stats.apps}</p><p className="text-gray-400">Apps</p></div>
        <div><p className="font-bold">{stats.installs.toLocaleString()}</p><p className="text-gray-400">Installs</p></div>
        <div><p className="font-bold">{stats.rating.toFixed(1)} ★</p><p className="text-gray-400">Rating</p></div>
      </div>
      {topApps.length > 0 && (
        <div className="mt-2 flex gap-1">
          {topApps.map(a => <span key={a.slug} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{a.name}</span>)}
        </div>
      )}
    </a>
  );
}
