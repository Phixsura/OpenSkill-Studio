"use client";

interface CommentInfo {
  comment_id: string;
  author: string;
  body: string;
  parent_id: string | null;
}

interface APIChangelogCommentCardProps {
  comments: CommentInfo[];
  entryTitle: string;
  appName: string;
}

export default function APIChangelogCommentCard({ comments, entryTitle, appName }: APIChangelogCommentCardProps) {
  const topLevel = comments.filter((c) => !c.parent_id);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Comments</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {entryTitle}</p>
        </div>
        <span className="text-xs text-gray-400">{comments.length} comments</span>
      </div>

      {comments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No comments</p>
      ) : (
        <div className="space-y-2">
          {topLevel.map((c) => {
            const replies = comments.filter((r) => r.parent_id === c.comment_id);
            return (
              <div key={c.comment_id}>
                <div className="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
                  <p className="text-[10px] font-medium text-gray-600 dark:text-gray-400">{c.author}</p>
                  <p className="text-xs text-gray-700 dark:text-gray-300">{c.body}</p>
                </div>
                {replies.map((r) => (
                  <div key={r.comment_id} className="ml-4 mt-1 rounded-lg bg-gray-50 px-3 py-1.5 dark:bg-gray-800">
                    <p className="text-[10px] text-gray-500">{r.author}: {r.body}</p>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
