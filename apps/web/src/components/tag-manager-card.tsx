"use client";

interface TagCount {
  tag: string;
  count: number;
}

interface TagManagerCardProps {
  tags: TagCount[];
  appName: string;
  totalResources: number;
}

function tagCategory(tag: string): string | null {
  const idx = tag.indexOf(":");
  return idx > 0 ? tag.slice(0, idx) : null;
}

const CATEGORY_COLORS: Record<string, string> = {
  env: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  team: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  priority: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  status: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
};

const DEFAULT_COLOR = "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";

export default function TagManagerCard({ tags, appName, totalResources }: TagManagerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Tags</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{tags.length} tags</span>
          <span className="text-xs text-gray-400">· {totalResources} resources</span>
        </div>
      </div>

      {tags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tags</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {tags.map((t) => {
            const cat = tagCategory(t.tag);
            const color = (cat && CATEGORY_COLORS[cat]) || DEFAULT_COLOR;
            return (
              <span
                key={t.tag}
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${color}`}
              >
                {t.tag}
                <span className="rounded-full bg-white/50 px-1.5 text-[10px] dark:bg-black/20">
                  {t.count}
                </span>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
