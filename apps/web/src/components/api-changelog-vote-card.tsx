"use client";

interface VoteInfo { entry_id: string; title: string; score: number; upvote_count: number; downvote_count: number; }
interface APIChangelogVoteCardProps { entries: VoteInfo[]; appName: string; }

export default function APIChangelogVoteCard({ entries, appName }: APIChangelogVoteCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👍 Changelog Votes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{entries.length} entries</span>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No votes yet</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.title}</span>
              <div className="flex items-center gap-2">
                <span className="text-green-600">+{e.upvote_count}</span>
                <span className="text-red-500">-{e.downvote_count}</span>
                <span className={`font-medium ${e.score >= 0 ? "text-green-600" : "text-red-500"}`}>{e.score}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
