"use client";

interface DeveloperProfile {
  id: string;
  name: string;
  avatar: string;
  bio: string;
  company: string;
  website: string;
  joinedAt: string;
  extensionCount: number;
  totalDownloads: number;
  avgRating: number;
  verified: boolean;
  badges: { name: string; icon: string }[];
  topExtensions: { name: string; downloads: number; rating: number }[];
}

export function DeveloperProfileCard({
  profile,
  onViewExtensions,
}: {
  profile: DeveloperProfile;
  onViewExtensions?: () => void;
}) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-md">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white text-center">
        <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-3xl mx-auto mb-2">
          {profile.avatar}
        </div>
        <h2 className="text-xl font-bold flex items-center justify-center gap-1">
          {profile.name}
          {profile.verified && <span title="Verified" className="text-sm">✓</span>}
        </h2>
        {profile.company && <p className="text-sm opacity-80">{profile.company}</p>}
      </div>

      <div className="p-5 space-y-4">
        {/* Bio */}
        <p className="text-sm text-gray-600 dark:text-gray-300">{profile.bio}</p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
            <div className="text-lg font-bold">{profile.extensionCount}</div>
            <div className="text-xs text-gray-500">Extensions</div>
          </div>
          <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
            <div className="text-lg font-bold">{profile.totalDownloads.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Downloads</div>
          </div>
          <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
            <div className="text-lg font-bold">★ {profile.avgRating.toFixed(1)}</div>
            <div className="text-xs text-gray-500">Avg Rating</div>
          </div>
        </div>

        {/* Badges */}
        {profile.badges.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {profile.badges.map((b) => (
              <span key={b.name} className="text-xs bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 px-2 py-1 rounded-full">
                {b.icon} {b.name}
              </span>
            ))}
          </div>
        )}

        {/* Top Extensions */}
        {profile.topExtensions.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold mb-2">Top Extensions</h3>
            {profile.topExtensions.map((ext) => (
              <div key={ext.name} className="flex justify-between text-sm py-1 border-b dark:border-gray-800 last:border-0">
                <span>{ext.name}</span>
                <span className="text-xs text-gray-400">⬇ {ext.downloads.toLocaleString()} · ★ {ext.rating}</span>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 text-sm">
          {profile.website && (
            <span className="text-blue-500">🔗 {profile.website}</span>
          )}
        </div>

        <button
          onClick={onViewExtensions}
          className="w-full rounded-lg border dark:border-gray-600 py-2 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          View All Extensions →
        </button>
      </div>
    </div>
  );
}
