"use client";
interface TagCount { tag: string; count: number; }
export function TagCloud({ tags, onSelect }: { tags: TagCount[]; onSelect?: (tag: string) => void }) {
  const max = Math.max(...tags.map(t => t.count), 1);
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">🏷️ Popular Tags</h2>
      <div className="flex flex-wrap gap-1">
        {tags.map((t) => {
          const size = 0.7 + (t.count / max) * 0.8;
          return (
            <button key={t.tag} onClick={() => onSelect?.(t.tag)}
              className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full hover:bg-blue-100"
              style={{ fontSize: `${size}rem` }}>{t.tag} <span className="text-xs text-gray-400">{t.count}</span></button>
          );
        })}
      </div>
    </div>
  );
}
