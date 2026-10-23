"use client";

interface ProfileApp { name: string; icon: string; rating: number; installs: number; }
interface DevProfileCardProps { name: string; bio: string; verified: boolean;
  joined: string; appCount: number; totalInstallsDisplay: string;
  avgRating: number; apps: ProfileApp[]; }

export function DevProfileCard({ name, bio, verified, joined, appCount,
  totalInstallsDisplay, avgRating, apps }: DevProfileCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-5 border-b dark:border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="text-lg font-bold">{name}</h3>
          {verified && <span className="text-blue-500" title="Verified">✓</span>}
        </div>
        <p className="text-sm text-gray-500 mb-3">{bio}</p>
        <div className="flex gap-4 text-xs text-gray-400">
          <span>📱 {appCount} apps</span>
          <span>📥 {totalInstallsDisplay} installs</span>
          <span>⭐ {avgRating} avg</span>
          <span>📅 Joined {joined}</span>
        </div>
      </div>
      <div className="p-4">
        <h4 className="text-xs font-semibold text-gray-400 mb-2">Apps</h4>
        <div className="flex gap-2">
          {apps.map(a => (
            <div key={a.name} className="w-20 text-center rounded-lg border dark:border-gray-700 p-2">
              <span className="text-xl">{a.icon}</span>
              <p className="text-xs font-medium truncate mt-0.5">{a.name}</p>
              <p className="text-[10px] text-gray-400">⭐ {a.rating}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
