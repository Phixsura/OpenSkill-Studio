"use client";

interface CommunityDashboardProps {
  forumDisplay: string; starsDisplay: string; forksDisplay: string;
  discordDisplay: string; twitterDisplay: string;
  blogPosts: number; communityApps: number; communityScore: string; }

export function CommunityDashboard({ forumDisplay, starsDisplay, forksDisplay,
  discordDisplay, twitterDisplay, blogPosts, communityApps, communityScore }: CommunityDashboardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🌍 Community</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
          communityScore === "vibrant" ? "bg-green-100 text-green-700" :
          communityScore === "active" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
        }`}>{communityScore}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { icon: "💬", value: forumDisplay, label: "Forum Activity" },
          { icon: "⭐", value: starsDisplay, label: "GitHub Stars" },
          { icon: "🍴", value: forksDisplay, label: "Forks" },
          { icon: "🎮", value: discordDisplay, label: "Discord" },
          { icon: "🐦", value: twitterDisplay, label: "Twitter" },
          { icon: "📝", value: String(blogPosts), label: "Blog Posts" },
        ].map(s => (
          <div key={s.label}>
            <p className="text-lg">{s.icon}</p>
            <p className="text-lg font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-3">{communityApps} community apps</p>
    </div>
  );
}
