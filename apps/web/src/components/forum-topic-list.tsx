"use client";

interface ForumTopic { title: string; author: string; category: string;
  replies: number; views: number; likes: number; solved: boolean; }
interface ForumTopicListProps { topics: ForumTopic[]; total: number;
  sort: string; onSelect: (title: string) => void; }

export function ForumTopicList({ topics, total, sort, onSelect }: ForumTopicListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💬 Forum</h3>
        <span className="text-xs text-gray-400">{total} topics · {sort}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {topics.map((t, i) => (
          <button key={i} onClick={() => onSelect(t.title)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-sm font-medium">{t.title}</span>
              {t.solved && <span className="text-xs text-green-600">✓ Solved</span>}
              <span className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded capitalize">{t.category}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{t.author}</span>
              <span>💬 {t.replies}</span>
              <span>👁️ {t.views}</span>
              <span>❤️ {t.likes}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
