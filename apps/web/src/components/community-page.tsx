"use client";

interface CommunityLink { id: string; name: string; icon: string; href: string; members: number; }
interface Discussion { title: string; author: string; replies: number; }
interface Contributor { name: string; contributions: number; badge: string; }
interface CommunityPageProps { links: CommunityLink[]; discussions: Discussion[];
  contributors: Contributor[]; totalMembers: number; }

export function CommunityPage({ links, discussions, contributors, totalMembers }: CommunityPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">💬 Developer Community</h1>
        <p className="text-sm text-gray-400">{totalMembers.toLocaleString()} members across all platforms</p>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {links.map(l => (
          <a key={l.id} href={l.href} target="_blank" rel="noopener"
            className="flex flex-col items-center gap-1 rounded-xl border p-4 text-center hover:shadow dark:border-gray-700">
            <span className="text-2xl">{l.icon}</span>
            <span className="text-sm font-medium">{l.name}</span>
            <span className="text-xs text-gray-400">{l.members.toLocaleString()} members</span>
          </a>
        ))}
      </div>
      {discussions.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Discussions</h2>
          {discussions.map((d, i) => (
            <div key={i} className="flex justify-between rounded border px-3 py-2 text-sm dark:border-gray-700 mb-1">
              <span>{d.title}</span>
              <span className="text-xs text-gray-400">{d.replies} replies</span>
            </div>
          ))}
        </div>
      )}
      {contributors.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">🏆 Top Contributors</h2>
          <div className="flex gap-3">
            {contributors.map((c, i) => (
              <div key={i} className="rounded-lg border px-3 py-2 text-center dark:border-gray-700">
                <span>{c.badge}</span>
                <p className="text-sm font-medium">{c.name}</p>
                <p className="text-xs text-gray-400">{c.contributions} contributions</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
