"use client";

interface Segment { name: string; count: number; pct: number; }
interface UserSegmentBreakdownProps { totalUsers: number; segments: Segment[]; }

const segmentLabels: Record<string, string> = {
  new_user: "🆕 New", onboarding: "🎯 Onboarding", established: "✅ Established",
  power_user: "⚡ Power User", active_user: "🔵 Active", contributor: "💬 Contributor",
  premium: "💎 Premium", paying: "💳 Paying", developer: "👨‍💻 Developer",
};

export function UserSegmentBreakdown({ totalUsers, segments }: UserSegmentBreakdownProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">User Segments</h2>
        <span className="text-sm text-gray-400">{totalUsers.toLocaleString()} total</span>
      </div>
      <div className="space-y-2">
        {segments.map(s => (
          <div key={s.name}>
            <div className="flex justify-between text-sm">
              <span>{segmentLabels[s.name] ?? s.name}</span>
              <span className="text-gray-400">{s.count} ({s.pct}%)</span>
            </div>
            <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${s.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
