"use client";

interface Tag { tag: string; count: number; weight: number; size: number; }
interface TagCloudProps { tags: Tag[]; onTagClick: (tag: string) => void; }

const colors = ["text-blue-500", "text-purple-500", "text-green-500", "text-orange-500",
  "text-pink-500", "text-cyan-500", "text-indigo-500"];

export function TagCloud({ tags, onTagClick }: TagCloudProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Popular Tags</h2>
      <div className="flex flex-wrap items-center gap-2">
        {tags.map((t, i) => (
          <button key={t.tag} onClick={() => onTagClick(t.tag)}
            className={`rounded-full border px-3 py-1 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800 ${colors[i % colors.length]}`}
            style={{ fontSize: `${t.size}px` }}>
            {t.tag}
            <span className="ml-1 text-[10px] text-gray-400">({t.count})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
