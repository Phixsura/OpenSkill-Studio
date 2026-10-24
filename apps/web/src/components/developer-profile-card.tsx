"use client";

interface DeveloperProfileCardProps { name: string; bio: string; avatarUrl: string;
  appsCount: number; downloadsDisplay: string; verified: boolean; badge: string;
  links: Record<string, string>; }

export function DeveloperProfileCard({ name, bio, avatarUrl, appsCount, downloadsDisplay,
  verified, badge, links }: DeveloperProfileCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-start gap-4">
        <img src={avatarUrl} alt={name} className="h-16 w-16 rounded-full" />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold">{name}</h3>
            {verified && <span className="text-blue-500">✓</span>}
          </div>
          <p className="text-xs text-gray-400">{badge}</p>
          {bio && <p className="mt-1 text-sm text-gray-500">{bio}</p>}
          <div className="mt-3 flex gap-4 text-sm">
            <div><span className="font-bold">{appsCount}</span> <span className="text-gray-400">apps</span></div>
            <div><span className="font-bold">{downloadsDisplay}</span> <span className="text-gray-400">downloads</span></div>
          </div>
          {Object.keys(links).length > 0 && (
            <div className="mt-2 flex gap-2">
              {Object.entries(links).map(([k, v]) => (
                <a key={k} href={v} target="_blank" rel="noopener" className="text-xs text-blue-600 hover:underline capitalize">{k}</a>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
