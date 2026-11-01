"use client";

interface DiscussionInfo { discussion_id: string; title: string; author: string; reply_count: number; resolved: boolean; }
interface Props { discussions: DiscussionInfo[]; appName: string; }

export default function APIDeveloperCommunityCard({ discussions, appName }: Props) {
  const open = discussions.filter((d) => !d.resolved).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Community</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{open} open / {discussions.length} total</span>
      </div>
      {discussions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No discussions</p>
      ) : (
        <div className="space-y-1">
          {discussions.map((d) => (
            <div key={d.discussion_id} className={`flex items-center justify-between text-[11px] ${d.resolved ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${d.resolved ? "bg-green-500" : "bg-blue-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{d.title}</span>
              </div>
              <span className="text-gray-400">{d.reply_count} replies</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
