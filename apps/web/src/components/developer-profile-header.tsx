"use client";

interface DeveloperStats { total_apps: number; total_installs: number; avg_rating: number; }
interface DeveloperProfileHeaderProps { displayName: string; bio: string; avatar?: string;
  joined?: string; verified: boolean; stats: DeveloperStats; }

export function DeveloperProfileHeader({ displayName, bio, avatar, joined, verified, stats }: DeveloperProfileHeaderProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        {avatar ? (
          <div className="h-16 w-16 rounded-full bg-gray-200 dark:bg-gray-700" />
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 text-2xl font-bold text-blue-600 dark:bg-blue-900/30">
            {displayName.charAt(0)}
          </div>
        )}
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold">{displayName}</h1>
            {verified && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">✓ Verified</span>}
          </div>
          <p className="text-sm text-gray-400">{bio}</p>
          {joined && <p className="text-xs text-gray-300">Joined {joined}</p>}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{stats.total_apps}</p><p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{stats.total_installs.toLocaleString()}</p><p className="text-xs text-gray-400">Installs</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">⭐ {stats.avg_rating}</p><p className="text-xs text-gray-400">Avg Rating</p>
        </div>
      </div>
    </div>
  );
}
