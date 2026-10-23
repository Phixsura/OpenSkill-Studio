"use client";

interface Tag { tag: string; count: number; }
interface TagCloudProps { tags: Tag[]; onTagClick: (tag: string) => void; activeTag?: string; }

export function TagCloud({ tags, onTagClick, activeTag }: TagCloudProps) {
  const maxCount = Math.max(...tags.map(t => t.count), 1);
  const getSize = (count: number) => {
    const ratio = count / maxCount;
    return ratio > 0.7 ? "text-lg font-bold" : ratio > 0.4 ? "text-base font-medium" : "text-sm";
  };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-500">Popular Tags</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {tags.map(t => (
          <button key={t.tag} onClick={() => onTagClick(t.tag)}
            className={`rounded-full px-3 py-1 transition ${getSize(t.count)} ${activeTag === t.tag
              ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"}`}>
            {t.tag}
            <span className="ml-1 text-xs opacity-60">({t.count})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
