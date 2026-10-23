"use client";

interface Badge { type: string; label?: string; icon?: string; }
interface DeveloperProfileHeaderProps {
  name: string; bio: string; verified: boolean; joinedAt: string;
  totalApps: number; totalInstalls: number; avgRating: number; badges: Badge[];
}

export function DeveloperProfileHeader({ name, bio, verified, joinedAt, totalApps, totalInstalls, avgRating, badges }: DeveloperProfileHeaderProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 p-6 dark:from-blue-900/10 dark:to-indigo-900/10">
      <div className="flex items-center gap-3">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-xl text-white">{name[0]}</div>
        <div>
          <h1 className="text-xl font-bold">{name} {verified && <span className="text-blue-600">✅</span>}</h1>
          <p className="text-sm text-gray-500">{bio}</p>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-4 gap-4 text-center">
        <div><p className="text-lg font-bold">{totalApps}</p><p className="text-xs text-gray-400">Apps</p></div>
        <div><p className="text-lg font-bold">{totalInstalls.toLocaleString()}</p><p className="text-xs text-gray-400">Installs</p></div>
        <div><p className="text-lg font-bold">{avgRating.toFixed(1)}</p><p className="text-xs text-gray-400">Rating</p></div>
        <div><p className="text-lg font-bold">{joinedAt.slice(0, 4)}</p><p className="text-xs text-gray-400">Joined</p></div>
      </div>
      {badges.length > 0 && (
        <div className="mt-3 flex gap-1">
          {badges.map((b, i) => <span key={i} className="rounded bg-white/60 px-2 py-0.5 text-xs dark:bg-gray-800">{b.icon || "🏅"} {b.label || b.type}</span>)}
        </div>
      )}
    </div>
  );
}
