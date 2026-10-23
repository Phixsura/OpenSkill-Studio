"use client";

interface CommunityStats { members: number; online: number; discussions: number; }
interface Discussion { title: string; pinned?: boolean; }
interface CommunityPageLayoutProps { stats: CommunityStats; pinned: Discussion[]; recent: Discussion[];
  categories: string[]; onNewDiscussion: () => void; children: React.ReactNode; }

export function CommunityPageLayout({ stats, pinned, recent, categories, onNewDiscussion, children }: CommunityPageLayoutProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Community</h1>
          <p className="text-sm text-gray-400">{stats.members.toLocaleString()} members · {stats.online} online</p>
        </div>
        <button onClick={onNewDiscussion} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white">
          + New Discussion
        </button>
      </div>
      <div className="flex gap-2">
        {categories.map(c => (
          <button key={c} className="rounded-full border border-gray-200 px-3 py-1 text-xs capitalize hover:bg-gray-50 dark:border-gray-700">
            {c}
          </button>
        ))}
      </div>
      {pinned.length > 0 && (
        <div className="space-y-1">
          {pinned.map((d, i) => (
            <div key={i} className="flex items-center gap-2 rounded bg-yellow-50 px-3 py-2 text-sm dark:bg-yellow-900/20">
              <span>📌</span> <span className="font-medium">{d.title}</span>
            </div>
          ))}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}
