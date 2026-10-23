"use client";

interface Member { name: string; score: number; rank: number; badge: string;
  forumPosts: number; appsPublished: number; }
interface CommunityLeaderboardProps { members: Member[]; period: string; }

export function CommunityLeaderboard({ members, period }: CommunityLeaderboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏆 Community Leaders</h3>
        <span className="text-xs text-gray-400 capitalize">{period}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {members.map(m => (
          <div key={m.name} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="w-6 text-center font-bold text-gray-300">{m.badge || m.rank}</span>
              <span className="text-sm font-medium">{m.name}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>💬 {m.forumPosts}</span>
              <span>📱 {m.appsPublished}</span>
              <span className="font-bold text-blue-600">{m.score} pts</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
