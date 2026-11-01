"use client";

interface ForumThread {
  threadId: string; title: string; author: string; tags: string[];
  replyCount: number; upvotes: number; answered: boolean; timestamp: string;
}

export function CommunityForumPanel({ threads, onUpvote, onSelect }: {
  threads: ForumThread[];
  onUpvote?: (id: string) => void;
  onSelect?: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">💬 Community Forum</h2>
      <div className="space-y-1">
        {threads.map((t) => (
          <div key={t.threadId} className="rounded-lg border dark:border-gray-700 p-3 flex gap-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50"
            onClick={() => onSelect?.(t.threadId)}>
            <button onClick={(e) => { e.stopPropagation(); onUpvote?.(t.threadId); }}
              className="flex flex-col items-center w-10 shrink-0 text-xs text-gray-500 hover:text-blue-600">
              <span>▲</span>
              <span className="font-bold">{t.upvotes}</span>
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{t.title}</span>
                {t.answered && <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">Answered</span>}
              </div>
              <div className="flex gap-2 text-xs text-gray-400 mt-0.5">
                <span>{t.author}</span>
                <span>💬 {t.replyCount}</span>
                <span>{t.timestamp}</span>
                {t.tags.map((tag) => <span key={tag} className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">{tag}</span>)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
