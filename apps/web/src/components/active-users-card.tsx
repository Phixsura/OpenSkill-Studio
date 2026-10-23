"use client";

interface ActiveUsersCardProps { dauDisplay: string; wauDisplay: string;
  mauDisplay: string; stickinessDisplay: string; engagement: string; }

const ENG_STYLE: Record<string, string> = {
  high: "text-green-600", medium: "text-yellow-600", low: "text-red-600",
};

export function ActiveUsersCard({ dauDisplay, wauDisplay, mauDisplay, stickinessDisplay, engagement }: ActiveUsersCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">👥 Active Users</h3>
      <div className="grid grid-cols-3 gap-3 text-center mb-3">
        <div><p className="text-xl font-bold">{dauDisplay}</p><p className="text-xs text-gray-400">DAU</p></div>
        <div><p className="text-xl font-bold">{wauDisplay}</p><p className="text-xs text-gray-400">WAU</p></div>
        <div><p className="text-xl font-bold">{mauDisplay}</p><p className="text-xs text-gray-400">MAU</p></div>
      </div>
      <div className="text-center">
        <span className={`text-sm font-medium ${ENG_STYLE[engagement] || ""}`}>
          {stickinessDisplay} stickiness · {engagement} engagement
        </span>
      </div>
    </div>
  );
}
