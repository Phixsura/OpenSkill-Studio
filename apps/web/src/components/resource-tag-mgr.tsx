"use client";

interface TaggedResource { id: string; tags: Record<string, string>; }
interface ResourceTagMgrProps { resources: TaggedResource[]; tagKeys: Record<string, number>; }

export function ResourceTagMgr({ resources, tagKeys }: ResourceTagMgrProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Resource Tags</h3>
        <span className="text-xs text-gray-400">{resources.length} resources · {Object.keys(tagKeys).length} tag keys</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {resources.map(r => (
          <div key={r.id} className="px-4 py-2 text-xs">
            <div className="font-mono font-semibold mb-1">{r.id}</div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(r.tags).map(([k, v]) => (
                <span key={k} className="px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px]">{k}={v}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
