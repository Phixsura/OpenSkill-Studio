"use client";

interface RecentApp { id: string; name: string; icon: string; }
interface UserProfilePageProps { name: string; email: string; avatarUrl: string;
  bio: string; role: string; memberSince: string;
  stats: { apps: number; totalInstalls: number; activityCount: number };
  recentApps: RecentApp[]; onSelectApp: (id: string) => void; }

export function UserProfilePage({ name, avatarUrl, bio, role, memberSince, stats, recentApps, onSelectApp }: UserProfilePageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-start gap-4">
        <img src={avatarUrl} alt={name} className="h-20 w-20 rounded-full" />
        <div>
          <h1 className="text-2xl font-bold">{name}</h1>
          <p className="text-sm text-gray-400 capitalize">{role} · Member since {memberSince}</p>
          {bio && <p className="mt-1 text-sm text-gray-500">{bio}</p>}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{stats.apps}</p><p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{stats.totalInstalls.toLocaleString()}</p><p className="text-xs text-gray-400">Installs</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{stats.activityCount}</p><p className="text-xs text-gray-400">Activities</p>
        </div>
      </div>
      {recentApps.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Apps</h2>
          <div className="flex gap-2">
            {recentApps.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm dark:border-gray-700">
                <span>{a.icon}</span>{a.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
