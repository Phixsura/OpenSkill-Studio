"use client";

interface TaggedResource { id: string; tags: Record<string, string>; }
interface ResourceTagManagerProps { resources: TaggedResource[];
  tagDistribution: Record<string, number>; onTag: (id: string) => void; }

export function ResourceTagManager({ resources, tagDistribution, onTag }: ResourceTagManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Resource Tags</h3>
        <span className="text-xs text-gray-400">{resources.length} resources</span>
      </div>
      <div className="flex gap-2 px-4 py-2 border-b dark:border-gray-700 flex-wrap">
        {Object.entries(tagDistribution).map(([tag, count]) => (
          <span key={tag} className="px-2 py-0.5 text-[10px] bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded">{tag}: {count}</span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {resources.map(r => (
          <div key={r.id} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-mono">{r.id}</span>
              <div className="flex gap-1 mt-0.5">
                {Object.entries(r.tags).map(([k, v]) => (
                  <span key={k} className="px-1.5 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">{k}={v}</span>
                ))}
              </div>
            </div>
            <button onClick={() => onTag(r.id)} className="text-xs text-blue-500 hover:underline">Edit Tags</button>
          </div>
        ))}
      </div>
    </div>
  );
}
