"use client";
export function FleetAiCommunityPanel({ forums, active, members, posts, resolved }: { forums: number; active: number; members: number; posts: number; resolved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 AI Community</h3>
    <div className="text-sm">{active}/{forums} active · {members.toLocaleString()} members · {posts} posts · {resolved}% resolved</div>
  </div>);
}
