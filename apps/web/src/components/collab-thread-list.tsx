"use client";

interface Thread { threadId: string; title: string; authorId: string; status: string; tags: string[]; messageCount: number; createdAt: number; }

const statusBadge: Record<string, string> = {
  open: "bg-green-100 text-green-700", resolved: "bg-gray-100 text-gray-500", locked: "bg-red-100 text-red-700",
};

export function CollabThreadList({ threads, onSelect, onCreate }: {
  threads: Thread[]; onSelect?: (id: string) => void; onCreate?: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Discussions ({threads.length})</h3>
        <button onClick={onCreate} className="text-xs bg-blue-500 text-white px-3 py-1 rounded-lg">+ New Thread</button>
      </div>
      {threads.map(t => (
        <button key={t.threadId} onClick={() => onSelect?.(t.threadId)}
          className="w-full text-left border dark:border-gray-700 rounded-xl p-3 hover:border-blue-400">
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm">{t.title}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${statusBadge[t.status] || ""}`}>{t.status}</span>
          </div>
          <div className="flex gap-2 mt-1 text-xs text-gray-500">
            <span>by {t.authorId}</span>
            <span>· {t.messageCount} messages</span>
            {t.tags.map(tag => <span key={tag} className="bg-blue-50 dark:bg-blue-900/10 text-blue-600 px-1 rounded">{tag}</span>)}
          </div>
        </button>
      ))}
    </div>
  );
}
