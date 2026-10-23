"use client";

interface Badge { id: string; label: string; icon: string; }
interface Summary { totalApps: number; installsDisplay: string; totalReviews: number;
  avgRating: number; topApp: string | null; }
interface DeveloperStatsPageProps { developer: string; memberSince: string;
  summary: Summary; badges: Badge[]; }

export function DeveloperStatsPage({ developer, memberSince, summary, badges }: DeveloperStatsPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">{developer}</h1>
        <p className="text-sm text-gray-400">Developer since {memberSince}</p>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{summary.totalApps}</p><p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{summary.installsDisplay}</p><p className="text-xs text-gray-400">Installs</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{summary.totalReviews}</p><p className="text-xs text-gray-400">Reviews</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">⭐ {summary.avgRating}</p><p className="text-xs text-gray-400">Avg Rating</p>
        </div>
      </div>
      {summary.topApp && <p className="text-center text-sm text-gray-400">🏆 Top app: <strong>{summary.topApp}</strong></p>}
      {badges.length > 0 && (
        <div className="flex justify-center gap-2">
          {badges.map(b => (
            <span key={b.id} className="flex items-center gap-1 rounded-full border px-3 py-1 text-xs dark:border-gray-700">
              {b.icon} {b.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
