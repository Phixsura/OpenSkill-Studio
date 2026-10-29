"use client";

interface PostInfo { post_id: string; title: string; category: string; status: string; reply_count: number; upvotes: number; author_id: string; }
interface Props { posts: PostInfo[]; unansweredCount: number; categoryCounts: Record<string, number>; appName: string; }

const catBadge: Record<string, string> = { question: "bg-blue-100 text-blue-700", discussion: "bg-green-100 text-green-700", announcement: "bg-purple-100 text-purple-700", showcase: "bg-yellow-100 text-yellow-700", bug_report: "bg-red-100 text-red-700" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForumCard({ posts, unansweredCount, categoryCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Community Forum</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unansweredCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">{unansweredCount} unanswered</span>}
      </div>
      {posts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No forum posts</p>
      ) : (
        <div className="space-y-2">
          {posts.slice(0, 5).map((p) => (
            <div key={p.post_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${catBadge[p.category] ?? ""}`}>{p.category}</span>
                  <span className="text-gray-700 dark:text-gray-300">{p.title}</span>
                </div>
                <span className="text-gray-400">↑{p.upvotes} · {p.reply_count} replies</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
