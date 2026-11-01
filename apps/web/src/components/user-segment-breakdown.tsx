"use client";

interface SegmentSummary { count: number; pct: number; }
interface UserSegmentBreakdownProps {
  totalUsers: number;
  summary: Record<string, SegmentSummary>;
}

const COLORS: Record<string, string> = {
  power_users: "bg-purple-500", new_users: "bg-blue-500",
  churning: "bg-red-500", unclassified: "bg-gray-400",
};
const LABELS: Record<string, string> = {
  power_users: "Power Users", new_users: "New Users",
  churning: "Churning", unclassified: "Unclassified",
};

export function UserSegmentBreakdown({ totalUsers, summary }: UserSegmentBreakdownProps) {
  const entries = Object.entries(summary).sort((a, b) => b[1].count - a[1].count);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-1">👥 User Segments</h3>
      <p className="text-xs text-gray-400 mb-3">{totalUsers.toLocaleString()} total users</p>
      <div className="flex h-4 rounded-full overflow-hidden mb-4">
        {entries.map(([k, v]) => (
          <div key={k} className={`${COLORS[k] || "bg-gray-300"}`} style={{ width: `${v.pct}%` }}
               title={`${LABELS[k] || k}: ${v.pct}%`} />
        ))}
      </div>
      <div className="space-y-2">
        {entries.map(([k, v]) => (
          <div key={k} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${COLORS[k] || "bg-gray-300"}`} />
              <span>{LABELS[k] || k}</span>
            </div>
            <span className="text-gray-500">{v.count.toLocaleString()} ({v.pct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
