"use client";

interface BadgeInfo {
  badge_id: string;
  label: string;
  status: string;
  color: string;
  views: number;
}

interface APIStatusBadgeCardProps {
  badges: BadgeInfo[];
  appName: string;
}

const colorMap: Record<string, string> = {
  green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500", blue: "bg-blue-500", gray: "bg-gray-500",
};

export default function APIStatusBadgeCard({ badges, appName }: APIStatusBadgeCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 Status Badges</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{badges.length} badges</span>
      </div>

      {badges.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No status badges</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {badges.map((b) => (
            <div key={b.badge_id} className="inline-flex items-center rounded-md overflow-hidden text-[11px]">
              <span className="bg-gray-700 px-2 py-0.5 text-white">{b.label}</span>
              <span className={`px-2 py-0.5 text-white ${colorMap[b.color] ?? "bg-gray-500"}`}>{b.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
