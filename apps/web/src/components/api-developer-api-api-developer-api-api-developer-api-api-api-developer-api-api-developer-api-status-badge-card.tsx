"use client";

interface BadgeInfo { badge_id: string; label: string; value: string; color: string; }
interface Props { badges: BadgeInfo[]; appName: string; }

const bColor: Record<string, string> = { green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500", blue: "bg-blue-500", gray: "bg-gray-500" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadgeCard({ badges, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Status Badges</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {badges.length} badges</p>
      </div>
      {badges.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No badges</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {badges.map((b) => (
            <div key={b.badge_id} className="flex overflow-hidden rounded text-[10px]">
              <span className="bg-gray-600 px-2 py-0.5 text-white">{b.label}</span>
              <span className={`px-2 py-0.5 text-white ${bColor[b.color] ?? "bg-gray-500"}`}>{b.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
